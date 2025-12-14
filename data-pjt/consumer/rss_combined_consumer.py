from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common import Configuration
import json
import os
from elasticsearch import Elasticsearch
import psycopg2
from datetime import datetime
from preprocess import (
    transform_extract_keywords,
    transform_to_embedding,
    transform_classify_category,
    splitfront,
    splitback
)
from dotenv import load_dotenv
from hdfs import InsecureClient
import time

# 환경 변수 로드
load_dotenv()

def create_kafka_source():
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic = os.getenv("KAFKA_TOPIC", "article")
    kafka_group = os.getenv("KAFKA_GROUP_ID", "flink-combined-group1")
    print(f"Kafka config - servers: {kafka_servers}, topic: {kafka_topic}, group: {kafka_group}")
    return KafkaSource.builder() \
        .set_bootstrap_servers(kafka_servers) \
        .set_topics(kafka_topic) \
        .set_group_id(kafka_group) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

def get_db_connection():
    """데이터베이스 연결을 생성하고 반환하는 함수"""
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError("DB_PASSWORD environment variable is required")
    pg_conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5434)),
        dbname=os.getenv("DB_NAME", "news"),
        user=os.getenv("DB_USERNAME", "ssafyuser"),
        password=db_password
    )
    return pg_conn

def get_es_connection():
    """Elasticsearch 연결을 생성하고 반환하는 함수"""
    es_host = os.getenv("ES_HOST", "localhost")
    es_port = os.getenv("ES_PORT", "9200")
    return Elasticsearch(f"http://{es_host}:{es_port}")

def get_hdfs_client():
    """HDFS 클라이언트를 생성하고 반환하는 함수"""
    hdfs_host = os.getenv("HDFS_HOST", "localhost")
    hdfs_port = os.getenv("HDFS_PORT", "9870")
    hdfs_user = os.getenv("HDFS_USER", "ssafy")
    return InsecureClient(f'http://{hdfs_host}:{hdfs_port}', user=hdfs_user)

def process_and_save_for_hdfs(article, keywords):
    """HDFS 저장용 데이터 처리 함수"""
    try:
        output_json = json.dumps({
            "write_date": article["write_date"],
            "keywords": keywords
        }, ensure_ascii=False)
        return output_json
    except Exception as e:
        print(f"[❌ HDFS 처리 실패] {e}")
        return None

def save_to_hdfs(article, keywords, client):
    """기사를 HDFS에 저장하는 함수"""
    try:
        processed_data = process_and_save_for_hdfs(article, keywords)
        if processed_data:
            # HDFS 디렉토리 경로
            hdfs_dir = '/user/hadoop'
            hdfs_path = f'{hdfs_dir}/articles.json'
            
            # 디렉토리가 없으면 생성
            if not client.status(hdfs_dir, strict=False):
                client.makedirs(hdfs_dir)
                print(f"[📁 HDFS 디렉토리 생성] {hdfs_dir}")
            
            # 파일이 존재하는지 확인
            file_exists = client.status(hdfs_path, strict=False) is not None
            
            # 최대 3번까지 retry
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # HDFS에 데이터 저장 (없으면 새로 생성, 있으면 append)
                    with client.write(hdfs_path, append=file_exists, overwrite=not file_exists) as writer:
                        writer.write(processed_data + '\n')
                        writer.flush()  # 버퍼 강제 비우기
                    
                    # lease가 해제될 때까지 잠시 대기
                    time.sleep(2)  # 2초 대기
                    
                    print(f"[✅ HDFS 저장 완료] {hdfs_path}")
                    return True
                except Exception as write_error:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"[⚠️ HDFS 저장 재시도 {retry_count}/{max_retries}] {write_error}")
                        time.sleep(3)  # 실패 시 3초 대기 후 재시도
                    else:
                        raise write_error
            
            return False
    except Exception as e:
        print(f"[❌ HDFS 저장 실패] {e}")
        return False

def process_and_save(article_json):
    """기사를 처리하고 모든 저장소에 저장하는 함수"""
    try:
        # JSON 파싱은 한 번만 수행
        article = json.loads(article_json)
        print("\n" + "="*50)
        print(f"제목: {article['title']}")
        print(f"작성자: {article['writer']}")
        print(f"작성일: {article['write_date']}")
        print(f"카테고리: {article['category']}")
        print(f"URL: {article['url']}")
        print("="*50 + "\n")

        # 전처리 (한 번만 수행)
        writer = splitfront(article["writer"]) or 'unknown'
        email = splitback(article["writer"])
        keywords = transform_extract_keywords(article["content"])
        print("[임베딩 변환 시작]")
        embedding = transform_to_embedding(article["content"])
        if embedding is None:
            print("[경고] 임베딩 변환 실패")
        else:
            print("[임베딩 변환 완료]")
        category = transform_classify_category(article["content"])
        current_time = datetime.now()

        # 데이터베이스 연결
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor()
        es = get_es_connection()
        hdfs_client = get_hdfs_client()

        try:
            # PostgreSQL에 저장
            print("[DB 저장 시작]")
            pg_cursor.execute("""
                INSERT INTO news_article (
                    title, writer, email, write_date, category, content, 
                    url, keywords, embedding, views, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    title = EXCLUDED.title,
                    writer = EXCLUDED.writer,
                    email = EXCLUDED.email,
                    write_date = EXCLUDED.write_date,
                    category = EXCLUDED.category,
                    content = EXCLUDED.content,
                    keywords = EXCLUDED.keywords,
                    embedding = EXCLUDED.embedding,
                    updated_at = EXCLUDED.updated_at
                RETURNING id
            """, (
                article["title"],
                writer,
                email,
                article["write_date"],
                category,
                article["content"],
                article["url"],
                json.dumps(keywords, ensure_ascii=False),
                embedding,
                0,
                current_time
            ))
            article_id = pg_cursor.fetchone()[0]
            pg_conn.commit()

            # Elasticsearch에 저장
            es_doc = {
                "id": article_id,
                "title": article["title"],
                "content": article["content"],
                "writer": writer,
                "category": category,
                "write_date": article["write_date"] + "+00:00",
                "keywords": keywords,
                "url": article["url"],
                "views": 0
            }

            es.update(
                index="news",
                id=str(article_id),
                body={
                    "doc": es_doc,
                    "doc_as_upsert": True
                }
            )

            # HDFS에 저장 (이미 파싱된 article과 keywords 사용)
            hdfs_success = save_to_hdfs(article, keywords, hdfs_client)

            if hdfs_success:
                print(f"[✅ 모든 저장소 저장 완료] {article['title']}")
            else:
                print(f"[⚠️ 일부 저장소 저장 실패] {article['title']}")

            return article_json

        except Exception as e:
            print(f"[❌ 저장 실패] {e}")
            pg_conn.rollback()
            return None
        finally:
            pg_cursor.close()
            pg_conn.close()

    except Exception as e:
        print(f"[❌ 처리 실패] {e}")
        return None

def main():
    print("\nInitializing Flink configuration...")
    config = Configuration()
    
    # JAR 파일 경로 설정 (환경변수 기반)
    flink_jar_path = os.getenv("FLINK_JAR_PATH")
    kafka_client_jar_path = os.getenv("KAFKA_CLIENT_JAR_PATH")
    
    print(f"JAR paths:")
    print(f"Flink JAR: {flink_jar_path}")
    print(f"Kafka Client JAR: {kafka_client_jar_path}")
    
    # JAR 파일 경로에 file:// 프로토콜 추가
    if flink_jar_path and not flink_jar_path.startswith('file://'):
        flink_jar_path = f'file://{flink_jar_path}'
    if kafka_client_jar_path and not kafka_client_jar_path.startswith('file://'):
        kafka_client_jar_path = f'file://{kafka_client_jar_path}'
    
    # 여러 JAR 파일을 세미콜론(;)으로 연결
    jar_paths = []
    if flink_jar_path:
        jar_paths.append(flink_jar_path)
    if kafka_client_jar_path:
        jar_paths.append(kafka_client_jar_path)
    if jar_paths:
        config.set_string("pipeline.jars", ";".join(jar_paths))
    
    print("\nSetting up Flink environment...")
    env = StreamExecutionEnvironment.get_execution_environment(config)
    
    # 병렬도 설정 (1로 설정하여 단일 스레드로 실행)
    env.set_parallelism(1)
    
    # Kafka 소스 생성
    print("Creating Kafka source...")
    kafka_source = create_kafka_source()
    
    print("Setting up data stream...")
    stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka Source"
    )
    
    # 데이터 처리 파이프라인
    processed_stream = stream \
        .map(process_and_save, output_type=Types.STRING()) \
        .filter(lambda x: x is not None)
    
    # Flink 작업 실행
    env.execute("Combined News Article Processing")

if __name__ == "__main__":
    main() 