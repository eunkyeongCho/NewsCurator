from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewsArticle
from .utils import get_es_client, index_article

@receiver(post_save, sender=NewsArticle)
def index_article_to_elasticsearch(sender, instance, created, **kwargs):
    """기사가 저장될 때 Elasticsearch에 인덱싱"""
    try:
        es = get_es_client()
        index_article(es, instance)
    except Exception as e:
        print(f"기사 인덱싱 중 오류 발생: {e}") 