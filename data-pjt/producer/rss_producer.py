import os
import time
import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
from kafka import KafkaProducer
import json

# 환경변수 로드
load_dotenv()

# Kafka 설정
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",  # Kafka 브로커 주소
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

TOPIC = "article"

# RSS URL (환경변수에서 가져오기, 복수 URL은 쉼표로 구분)
RSS_FEED_URLS_STR = os.getenv("RSS_FEED_URLS")
if not RSS_FEED_URLS_STR:
    raise ValueError("RSS_FEED_URLS environment variable is required. Example: RSS_FEED_URLS=url1,url2,url3")

# 쉼표로 구분된 문자열을 리스트로 변환
RSS_FEED_URLS = [url.strip() for url in RSS_FEED_URLS_STR.split(",") if url.strip()]

if not RSS_FEED_URLS:
    raise ValueError("RSS_FEED_URLS must contain at least one valid URL")

# 중복 체크를 위한 URL 메모리 캐시
existing_urls = set()

# 본문 크롤링 함수
def crawq_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    content_tag = soup.select('p.content_text, p.content_text.text-l')
    content_text = "\n\n".join([tag.text.strip() for tag in content_tag])
    return content_text

# 새 데이터 수집 및 Kafka 전송
def fetch_and_send_articles():
    if not RSS_FEED_URLS:
        print("[⚠️ RSS 피드 URL이 설정되지 않았습니다]")
        return
    
    total_new_count = 0
    
    # 여러 RSS 피드를 순회하며 처리
    for feed_url in RSS_FEED_URLS:
        try:
            print(f"[RSS 피드 처리] {feed_url}")
            feed = feedparser.parse(feed_url)
            new_count = 0

            for entry in reversed(feed.entries):
                url = entry.link
                if url in existing_urls:
                    print(f"[건너뜀] 이미 존재하는 기사: {url}")
                    continue

                title = entry.title
                writer = entry.get('author', 'unknown')
                write_date = datetime(*entry.updated_parsed[:6]).isoformat()
                category = entry.tags[0].term if 'tags' in entry and entry.tags else '기타'
                content = crawq_article(url)

                article = {
                    "title": title,
                    "writer": writer,
                    "email": None,  # 전처리 전이므로 None
                    "write_date": write_date,
                    "category": category,
                    "content": content,
                    "url": url,
                    "keywords": [],
                    "embedding": None
                }

                # Kafka에 전송
                producer.send(TOPIC, article)
                existing_urls.add(url)
                new_count += 1
                total_new_count += 1
                print(f"[Kafka 전송] {title}")
            
            if new_count > 0:
                print(f"[✔] {feed_url}에서 {new_count}개 기사 전송 완료")
        except Exception as e:
            print(f"[⚠️ RSS 피드 처리 실패] {feed_url}: {e}")
            continue

    if total_new_count > 0:
        print(f"[✔] 총 {total_new_count}개 기사 전송 완료\n")
    else:
        print("[INFO] 새로운 기사가 없습니다.\n")

# 메인 루프 (10분마다 실행)
if __name__ == "__main__":
    print("[시작] 10분마다 RSS 피드 체크 중 (Kafka 전송)...\n")
    while True:
        try:
            fetch_and_send_articles()
        except Exception as e:
            print(f"[오류 발생] {e}")
        print("[로딩] 다음 체크까지 대기 중...\n")
        time.sleep(600)
