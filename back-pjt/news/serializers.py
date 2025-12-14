from rest_framework import serializers
from .models import NewsArticle, ArticleLike, ArticleBookmark
import ast


# 전제 뉴스 기사 목록 제공
class ArticleListSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    def get_keywords(self, obj):
        # print("DEBUG >>> obj.keywords:", repr(obj.keywords))
        try:
            # 문자열일 경우 파싱
            if isinstance(obj.keywords, str):
                cleaned = obj.keywords.strip()
                if cleaned in ("", "[]"):
                    return []
                return ast.literal_eval(cleaned)
            # 이미 리스트일 경우 그대로 반환
            elif isinstance(obj.keywords, list):
                return obj.keywords
        except Exception as e:
            print("ERROR >>>", e)
        return []

    def get_likes(self, obj):
        return ArticleLike.objects.filter(article=obj).count()
    
    class Meta:
        model = NewsArticle
        fields = ('id', 'title', 'writer', 'email', 'write_date', 'category', 'content', 'url', 'keywords','likes','views')

# 뉴스 기사 하나만 제공
class ArticleDetailSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    def get_keywords(self, obj):
        # print("DEBUG >>> obj.keywords:", repr(obj.keywords))
        try:
            # 문자열일 경우 파싱
            if isinstance(obj.keywords, str):
                cleaned = obj.keywords.strip()
                if cleaned in ("", "[]"):
                    return []
                return ast.literal_eval(cleaned)
            # 이미 리스트일 경우 그대로 반환
            elif isinstance(obj.keywords, list):
                return obj.keywords
        except Exception as e:
            print("ERROR >>>", e)
        return []
    
    def get_likes(self, obj):
        return ArticleLike.objects.filter(article=obj).count()
    
    def get_is_like(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_authenticated:
            return int(ArticleLike.objects.filter(user=user, article = obj).exists())
        return 0

    def get_is_bookmarked(self, obj):
        user = self.context['request'].user
        return ArticleBookmark.objects.filter(user=user, article=obj).exists()

    class Meta:
        model = NewsArticle
        fields = ('id', 'title', 'writer', 'email', 'write_date', 'category', 'content', 'url', 'keywords', 'likes','is_like','views','is_bookmarked')



#AritleLike 테이블을 채우는 toggle_like view함수용 시리얼라이저
class ArticleLikeSerializer(serializers.ModelSerializer):
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=NewsArticle.objects.all(),    # NewsArticle에 해당 기사 id 존재하는지 조회
        source='article',   #있다면 ArticleLike의 article 필드에 넣어줌
        write_only=True
    )

    def create(self, validated_data):
        user = self.context['request'].user
        article = validated_data['article']

        like_obj, created = ArticleLike.objects.get_or_create(
            user=user,
            article=article
        )
        return like_obj

    class Meta:
        model = ArticleLike
        fields = ['article_id']

#ArticleBookmark 테이블을 채우는 toggle_bookmark view함수용 시리얼라이저
class ArticleBookmarkSerializer(serializers.ModelSerializer):
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=NewsArticle.objects.all(),     #NewsArticle에 해당 기사 id 존재하는지 조회
        source='article',                      #있다면 ArticleBookmark의 article 필드에 넣어줌
        write_only=True
    )

    def create(self, validated_data):
        user = self.context['request'].user
        article = validated_data['article']
        
        bookmark_obj, created = ArticleBookmark.objects.get_or_create(
            user=user,
            article=article
        )
        return bookmark_obj

    class Meta:
        model = ArticleBookmark
        fields = ['id', 'article_id', 'created_at']
        read_only_fields = ['id', 'created_at']


# 대시보드용 통합 시리얼라이저
class DashboardSerializer(serializers.Serializer):
    class CategoryStateSerializer(serializers.Serializer):
        category = serializers.CharField()
        count = serializers.IntegerField()

    class KeywordStateSerializer(serializers.Serializer):
        keyword = serializers.CharField()
        score = serializers.FloatField()

    class DailyReadSerializer(serializers.Serializer):
        day = serializers.DateField()
        count = serializers.IntegerField()

    #나의 관심 카테고리: [{ "category": str, "count": int }]
    top_categories = CategoryStateSerializer(many = True)

    #주요 키워드: [{ "keyword": str, "score": float }]
    top_keywords = KeywordStateSerializer(many = True)

    #일별 읽은 기사 수(일주일치 표시): [{"daily": date, "count": int }]
    weekly_read_count = DailyReadSerializer(many = True)

    # 좋아요 누른 기사
    liked_articles = ArticleListSerializer(many=True)