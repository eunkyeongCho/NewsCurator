from django.db import models
from django.contrib.auth import get_user_model
import json
import numpy as np

# 유저 모델 생성
User = get_user_model()
# Create your models here.

class NewsArticle(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)  # DB에 있으니까 추가 (nullable)
    write_date = models.DateTimeField()
    category = models.CharField(max_length=50)
    content = models.TextField()
    url = models.URLField(unique=True)
    keywords = models.TextField()  # 그대로 TextField 유지
    embedding = models.BinaryField(null=True)
    views = models.IntegerField(default=0)
    updated_at = models.DateTimeField()

    @property
    def keywords_as_list(self):
        try:
            return json.loads(self.keywords)
        except Exception:
            return []

    def set_embedding(self, embedding_array):
        """numpy 배열을 바이너리 형태로 변환하여 저장"""
        if embedding_array is None:
            self.embedding = None
            return
            
        if isinstance(embedding_array, np.ndarray):
            embedding_array = embedding_array.tolist()
        
        embedding_json = json.dumps(embedding_array)
        self.embedding = embedding_json.encode('utf-8')

    def get_embedding(self):
        """저장된 바이너리 임베딩을 numpy 배열로 변환"""
        if self.embedding is None:
            return None
            
        try:
            embedding_str = self.embedding.tobytes().decode('utf-8')
            return np.array(json.loads(embedding_str), dtype=np.float32)
        except Exception as e:
            print(f"임베딩 변환 실패: {e}")
            return None

    class Meta:
        db_table = "news_article"  # 실제 DB 테이블명 명시
        managed = True     # 마이그레이션에서 관리하도록 변경



# 좋아요 테이블 구조
class ArticleLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)


    class Meta:
        unique_together = ('user', 'article')



# 조회 테이블 구조
class ArticleRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'article_read'

# 북마크 테이블 구조
class ArticleBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        db_table = 'article_bookmark'
