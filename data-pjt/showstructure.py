import os
import time
import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import json

# 환경변수 로드
load_dotenv()

# RSS URL
RSS_FEED_URL = "https://www.khan.co.kr/rss/rssdata/total_news.xml"
JSON_PATH = "rss_output.json"

# 본문 크롤링 함수
def crawq_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    content_tag = soup.find_all('p', class_="content_text text-l")
    content_text = "\n\n".join([tag.text.strip() for tag in content_tag])
    return content_text

# 기존 JSON 로딩 함수
def load_existing_articles():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 새 데이터 수집 및 저장 함수
def update_json_with_new_articles():
    existing_articles = load_existing_articles()
    existing_urls = {article["url"] for article in existing_articles}

    feed = feedparser.parse(RSS_FEED_URL)
    new_articles = []

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
        keywords = []
        embedding = None
        email = None  # 아직 분리 전

        article = {
            "title": title,
            "writer": writer,
            "email": email,
            "write_date": write_date,
            "category": category,
            "content": content,
            "url": url,
            "keywords": keywords,
            "embedding": embedding
        }

        new_articles.append(article)
        print(f"[추가됨] {title}")

    if new_articles:
        all_articles = existing_articles + new_articles
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        print(f"[✔] 저장 완료: {len(new_articles)}개 기사 추가됨\n")
    else:
        print("[INFO] 새로운 기사가 없습니다.\n")

# 메인 루프
if __name__ == "__main__":
    print("[시작] 10분마다 RSS 피드 체크 중...\n")
    while True:
        try:
            update_json_with_new_articles()
            print("새로 RSS피드 업데이트!")
        except Exception as e:
            print(f"[오류 발생] {e}")
        print("[로딩] 10분마다 RSS 피드 체크 중...\n")
        time.sleep(600)  # 10분 = 600초
        
