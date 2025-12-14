from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import NewsArticle, ArticleLike, ArticleRead, ArticleBookmark
from .serializers import ArticleListSerializer, ArticleDetailSerializer, ArticleLikeSerializer, DashboardSerializer, ArticleBookmarkSerializer
from django.db.models import F, Count
from django.db.models.functions import TruncDate
from django.db.models.expressions import RawSQL
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json, ast
from .utils import get_es_client, create_news_index, index_article, search_articles
from .chatbot.news_chatbot import get_newsbot_response, message_to_dict, message_from_dict
from django.contrib.auth import get_user_model


#모든 뉴스 리스트 보기. 권한 불필요
@api_view(['GET'])
def show_articles(request):

    queryset = NewsArticle.objects.all().order_by('-write_date')
    serializer = ArticleListSerializer(queryset, many= True)

    return Response(serializer.data)


def transform_embedding(embedding_binary):
    """임베딩 바이너리 데이터를 numpy 배열로 변환"""
    try:
        if embedding_binary is None:
            return None
        embedding_str = embedding_binary.tobytes().decode('utf-8')
        return np.array(json.loads(embedding_str), dtype=np.float32)
    except Exception as e:
        print(f"임베딩 변환 실패: {e}")
        return None

# =====================================================================================

#한 뉴스 자세히 보기 기능. 권한 필요
@api_view(['GET'])
def article_detail_view(request, id_pk):

    # 유저 진위성 파악
    if not request.user or not request.user.is_authenticated:
        return Response(
            {"message": "회원만 조회가능합니다. 로그인해주십시오."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 기사 존재 파악
    try:
        article = NewsArticle.objects.get(pk=id_pk)
    except NewsArticle.DoesNotExist:
        return Response(
            {"error": "해당 기사가 존재하지 않습니다."},
            status=status.HTTP_404_NOT_FOUND
        )

    #조건 만족시 조회수 증가
    article.views = F('views') + 1
    article.save(update_fields = ['views'])
    article.refresh_from_db()

    #조회 테이블에 기록 남기기
    ArticleRead.objects.create(user=request.user, article=article)

    #연관 기사 추출
    related_article = []
    base_vec = article.get_embedding()
    if base_vec is not None:
        try:
            base_vec = base_vec.reshape(1, -1)
            candidates = NewsArticle.objects.exclude(id=id_pk).exclude(embedding=None)

            similarities = []
            for other in candidates:
                try:
                    vec = other.get_embedding()
                    if vec is not None:
                        vec = vec.reshape(1, -1)
                        sim = cosine_similarity(base_vec, vec)[0][0]
                        similarities.append((sim, other))
                except Exception as e:
                    print(f"후보 기사 임베딩 변환 실패 {other.id}: {e}")
                    continue

            similarities.sort(reverse=True, key=lambda x: x[0])
            top_articles = [a for _, a in similarities[:5]]
            related_article = ArticleListSerializer(top_articles, many=True, context={'request': request}).data

        except Exception as e:
            print(f'유사도 계산 실패: {e}')

    # 응답 데이터 구성
    serializer = ArticleDetailSerializer(article, context={'request': request})
    response_data = {
        'article': serializer.data,
        'related_articles': related_article
    }

    return Response(response_data)


# 좋아용 누르기 기능. 권한 필요
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, id_pk):
    user = request.user

    try:
        article = NewsArticle.objects.get(pk = id_pk)
    except NewsArticle.DoesNotExist:
        return Response({'error':'해당 기사가 사라졌어요!'}, status = 404)
    
    # 좋아요가 이미 존재하는지 확인
    existing_like = ArticleLike.objects.filter(user=user, article=article).first()

    if existing_like:
        existing_like.delete()
        return Response(status = 204)
    else:
        serializer = ArticleLikeSerializer(data = {'article_id':article.id}, context = {'request':request})

        # 유효성 검사
        if serializer.is_valid():
            serializer.save()
            return Response(status = 201)
        else:
            return Response(status = 400)

# 북마크 누르기 기능. 권한 필요
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_bookmark(request, id_pk):
    user = request.user
    article = NewsArticle.objects.get(pk = id_pk)
    
    # 북마크를 이미 했는지 확인
    existing_bookmark = ArticleBookmark.objects.filter(user=user, article=article).first()

    if existing_bookmark:
        existing_bookmark.delete()
        return Response(status = 204)
    else:
        serializer = ArticleBookmarkSerializer(data = {'article_id':article.id}, context = {'request':request})

        # 유효성 검사
        if serializer.is_valid():
            serializer.save()
            return Response(status = 201)
        else:
            return Response(serializer.errors, status = 400)


# 뉴비 챗봇 사용
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_chatbot(request, id_pk):
    user = request.user
    article = NewsArticle.objects.get(pk = id_pk)
    question = request.data.get('question')


    if not question:
        return Response({"message": "질문을 입력해주세요."}, status = 400)

    # 세션에 이전 메시지 불러오기
    session_key = f"chat_history_{user.id}_{article.id}"
    messages = [message_from_dict(d) for d in request.session.get(session_key, [])]

    # 답변 작성
    answer, updated_messages = get_newsbot_response(
        messages,
        article.title,
        str(article.write_date),
        article.content,
        question
    )

    # 세션에 메시지 저장(직렬화 없이)
    request.session[session_key] = [message_to_dict(m) for m in updated_messages]
    request.session.modified = True  # 변경 감지.


    return Response({
        "history": [message_to_dict(m) for m in updated_messages if message_to_dict(m)["type"] != "system"]
    })



# 뉴비 챗봇 초기화
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_chatbot(request, id_pk):
    user = request.user
    article = NewsArticle.objects.get(pk = id_pk)
    session_key = f"chat_history_{user.id}_{article.id}"
    
    if session_key in request.session:
        del request.session[session_key]
        request.session.modified = True

    return Response({"message": "대화가 초기화되었습니다."})

#=============================================================================================

# 유저 정보 보기
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    return Response({
        "username": user.username,
        "user_id": user.id,
    })

# 유저의 북마크 목록 보기
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmark_list(request):
    user = request.user
    # 북마크 목록 가져오기
    bookmarks = ArticleBookmark.objects.filter(user=user).select_related('article')
    articles = [bookmark.article for bookmark in bookmarks]
    
    # 유저 정보와 북마크 목록을 함께 직렬화
    response_data = {
        "user": {
            "username": user.username,
        },
        "bookmarks": ArticleDetailSerializer(articles, many=True, context={'request': request}).data
    }
    
    return Response(response_data)


# ===============================================================================================
#유저의 대시보드. 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request, user_id):
    user = request.user

    # 1. 많이 본 카테고리(좋아요 기반)
    top_categories = (
        NewsArticle.objects
        .filter(articlelike__user=user)
        .values('category')
        .annotate(count = Count('id'))
        .order_by('-count')[:5]
    )

    top_categories_list = [
        {"category": c["category"], "count": c["count"]}
        for c in top_categories
    ]

    #-----------------------------------------------------

    #2. 주요 키워드(조회수 기반)
    read_articles_id = (
        ArticleRead.objects
        .filter(user=request.user)
        .values_list('article_id', flat = True)
        .distinct()
    )

    read_articles = NewsArticle.objects.filter(id__in=read_articles_id)

    all_keywords = []
    for article in read_articles:
        try:
            if isinstance(article.keywords, str):
                keywords = ast.literal_eval(article.keywords)
            else:
                keywords = article.keywords  # 혹시나 리스트일 수도 있음
            all_keywords += keywords
        except Exception as e:
            print(f"❌ 파싱 실패: {article.id}", e)
            continue


    #상위 5개 뽑기
    keywords_5 = Counter(all_keywords).most_common(5)
    # 정규화 과정. 최대 조회수를 기준으로 나누기
    max_count = keywords_5[0][1] if keywords_5 else 1

    main_keywords_list = [{"keyword": kw, "score": round(count / max_count, 2)} for kw, count in keywords_5]

    #---------------------------------------------------------

    # 3. 주간 읽은 기사(조회수 기반)
    last_7_days = timezone.now().date() - timedelta(days=6)
    daily_reads = (
        ArticleRead.objects
        .filter(user=user, read_at__date__gte=last_7_days)
        .annotate(day=TruncDate('read_at'))
        .values('day', 'article') # 유저 + 날짜 + 기사 단위로 유니크하게
        .distinct()
        .values('day')   # 날짜 기준만 남기고
        .annotate(count = Count('article'))  # 그 날짜에 유니크한 기사 수 세기
        .order_by('day')
    )

    weekly_read_count_list = [
        {"day": day['day'], "count": day['count']}
        for day in daily_reads
    ]

    #---------------------------------------------------------

    # 4. 좋아요 누른 기사들
    liked_articles = NewsArticle.objects.filter(articlelike__user = user)


    serializer = DashboardSerializer({
        'top_categories':top_categories_list,
        'top_keywords':main_keywords_list,
        'weekly_read_count': weekly_read_count_list,
        'liked_articles':liked_articles
    }, context={'request':request})


    return Response(serializer.data)


#=====================================================================================
# 개인 맞춤 알고리즘
# 좋아요 0.7 + 조회수 0.3 비율 기반

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personalized_recommendation(request):
    user = request.user

    # 1. 사용자 행동 기사 ID 가져오기
    like_articles = NewsArticle.objects.filter(articlelike__user=user).exclude(embedding=None)
    read_articles = (
        NewsArticle.objects.filter(articleread__user=user)
        .exclude(id__in=like_articles.values_list('id', flat=True))
        .exclude(embedding=None)
    )

    # 2. 임베딩 벡터 평균 계산
    like_vectors = []
    read_vectors = []

    # 좋아요한 기사들의 임베딩
    for article in like_articles:
        vec = article.get_embedding()
        if vec is not None:
            like_vectors.append(vec)

    # 읽은 기사들의 임베딩
    for article in read_articles:
        vec = article.get_embedding()
        if vec is not None:
            read_vectors.append(vec)

    # 3. 가중 평균 계산
    if like_vectors:
        like_vec = np.mean(like_vectors, axis=0)
    else:
        like_vec = None

    if read_vectors:
        read_vec = np.mean(read_vectors, axis=0)
    else:
        read_vec = None

    if read_vec is not None and like_vec is not None:
        user_vec = (read_vec * 0.3) + (like_vec * 0.7)
    elif like_vec is not None:
        user_vec = like_vec
    elif read_vec is not None:
        user_vec = read_vec
    else:
        return Response({"message": "추천할 행동 데이터가 부족합니다"}, status=400)

    # 4. 모든 기사와 유사도 계산
    candidates = NewsArticle.objects.exclude(
        id__in=like_articles.values_list('id', flat=True)
    ).exclude(embedding=None)

    similarities = []
    for article in candidates:
        article_vec = article.get_embedding()
        if article_vec is not None:
            sim = cosine_similarity(user_vec.reshape(1, -1), article_vec.reshape(1, -1))[0][0]
            similarities.append((sim, article))

    # 상위 10개 추천
    similarities.sort(reverse=True, key=lambda x: x[0])
    recommended_articles = [article for _, article in similarities[:10]]

    serializer = ArticleListSerializer(recommended_articles, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def search_news(request):
    """뉴스 검색 API"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', None)
    sort_by = request.GET.get('sort', None)
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))

    if not query:
        return Response(
            {"error": "검색어를 입력해주세요."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        es = get_es_client()
        search_result = search_articles(
            client=es,
            query=query,
            category=category,
            sort_by=sort_by,
            page=page,
            size=size
        )

        hits = search_result['hits']['hits']
        total = search_result['hits']['total']['value']

        results = []
        for hit in hits:

            source = hit['_source']
            highlight = hit.get('highlight', {})
            
            # 하이라이트된 제목과 내용 가져오기
            title = highlight.get('title', [source['title']])[0]
            content_preview = highlight.get('content', [source['content'][:150] + "..."])[0]
            
            results.append({
                'id': hit['_id'],  # _source의 id 대신 문서의 _id 사용
                'title': title,
                'content_preview': content_preview,
                'category': source['category'],
                'writer': source['writer'],
                'write_date': source['write_date'],
                'views': source['views'],
                'url': source['url'],
                'score': hit['_score']
            })

        return Response({
            'total': total,
            'page': page,
            'size': size,
            'results': results
        })

    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return Response(
            {"error": "검색 중 오류가 발생했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def index_all_articles(request):
    """모든 기사를 Elasticsearch에 인덱싱"""

    try:

        es = get_es_client()
        create_news_index(es)

        articles = NewsArticle.objects.all()

        for article in articles:
            index_article(es, article)

            
        return Response({"message": f"{articles.count()}개의 기사가 인덱싱되었습니다."})
    
    except Exception as e:
        print(f"인덱싱 중 오류 발생: {e}")
        return Response(
            {"error": "인덱싱 중 오류가 발생했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )