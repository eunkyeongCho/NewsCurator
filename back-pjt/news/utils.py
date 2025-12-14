from elasticsearch import Elasticsearch
from django.conf import settings
import json
import os

def get_es_client():
    """Elasticsearch 클라이언트 인스턴스를 반환"""
    es_host = os.getenv('ES_HOST', 'elasticsearch')
    es_port = os.getenv('ES_PORT', '9200')
    return Elasticsearch([f'http://{es_host}:{es_port}'])

def create_news_index(client):
    """뉴스 기사를 위한 인덱스 생성"""
    index_body = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "korean": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer",
                        "filter": ["nori_readingform", "lowercase"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "title": {
                    "type": "text",
                    "analyzer": "korean",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "korean"
                },
                "writer": {"type": "keyword"},
                "category": {"type": "keyword"},
                "write_date": {"type": "date"},
                "keywords": {"type": "keyword"},
                "url": {"type": "keyword"},
                "views": {"type": "integer"}
            }
        }
    }
    
    if not client.indices.exists(index="news"):
        client.indices.create(index="news", body=index_body)

def index_article(client, article):
    """기사를 Elasticsearch에 인덱싱"""
    try:
        keywords = json.loads(article.keywords) if isinstance(article.keywords, str) else article.keywords
    except:
        keywords = []
        
    doc = {
        'id': article.id,
        'title': article.title,
        'content': article.content,
        'writer': article.writer,
        'category': article.category,
        'write_date': article.write_date,
        'keywords': keywords,
        'url': article.url,
        'views': article.views
    }
    
    client.index(index="news", id=article.id, body=doc)

def clean_url_based_documents(client):
    """URL을 ID로 사용하는 문서들을 삭제"""
    try:
        client.delete_by_query(
            index="news",
            body={
                "query": {
                    "bool": {
                        "must_not": [
                            {"exists": {"field": "id"}}
                        ]
                    }
                }
            }
        )
    except Exception as e:
        print(f"URL 기반 문서 삭제 중 오류 발생: {e}")

def search_articles(client, query, category=None, sort_by=None, page=1, size=10):
    """기사 검색 실행"""
    # 검색 전 URL 기반 문서 정리
    clean_url_based_documents(client)
    
    must_conditions = [
        {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "content", "keywords^1.5"],
                "type": "most_fields"
            }
        }
    ]
    
    if category:
        must_conditions.append({"term": {"category": category}})
    
    body = {
        "query": {
            "bool": {
                "must": must_conditions
            }
        },
        "from": (page - 1) * size,
        "size": size,
        "highlight": {
            "fields": {
                "title": {},
                "content": {"fragment_size": 150, "number_of_fragments": 1}
            }
        }
    }
    
    if sort_by == "date":
        body["sort"] = [{"write_date": "desc"}]
    elif sort_by == "views":
        body["sort"] = [{"views": "desc"}]
    
    return client.search(index="news", body=body) 