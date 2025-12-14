# 뉴스 데이터 파이프라인

뉴스 데이터의 수집, 처리, 분석을 위한 데이터 파이프라인 시스템입니다. Kafka를 기반으로 한 실시간 데이터 스트리밍과 Airflow, Spark를 활용한 배치 처리를 제공합니다.

## 기술 스택

### 실시간 데이터 처리
- Apache Kafka
- Apache Flink
- Python 3.10

### 배치 처리
- Apache Airflow
- Apache Spark
- Python 3.10

### 컨테이너화
- Docker
- Docker Compose

## 프로젝트 구조

```
data-pjt/
├── producer/                    # Kafka 프로듀서
│   ├── rss_producer.py         # RSS 피드 수집기
│   ├── requirements.txt        # 프로듀서 의존성
│   ├── Dockerfile             # 프로듀서 도커 설정
│   ├── entrypoint.sh          # 컨테이너 진입점
│   └── wait-for-it.sh         # 서비스 의존성 체크
│
├── consumer/                    # Kafka 컨슈머
│   ├── rss_combined_consumer.py # 메인 컨슈머
│   ├── preprocess.py           # 데이터 전처리
│   ├── jargroup/              # 전문용어 처리
│   ├── requirements.txt        # 컨슈머 의존성
│   └── Dockerfile             # 컨슈머 도커 설정
│
├── batch/                      # 배치 처리
│   ├── dags/                  # Airflow DAG 정의
│   ├── logs/                  # Airflow 로그
│   ├── Dockerfile.airflow     # Airflow 도커 설정
│   ├── Dockerfile.spark       # Spark 도커 설정
│   └── start.sh              # 배치 서비스 시작 스크립트
│
└── docker/                     # 도커 관련 설정
```

## 시작하기

### 사전 요구사항
- Docker
- Docker Compose
- Python 3.10
- Kafka (Zookeeper 포함)
- Elasticsearch

### 전체 서비스 실행

1. 도커 컴포즈로 전체 서비스 실행
```bash
docker-compose up -d
```

2. 개별 서비스 실행
```bash
# 프로듀서 실행
cd producer
docker build -t news-producer .
docker run -d --name news-producer news-producer

# 컨슈머 실행
cd consumer
docker build -t news-consumer .
docker run -d --name news-consumer news-consumer

# 배치 서비스 실행
cd batch
./start.sh
```

## 주요 기능

### 1. 데이터 수집 (Producer)
- RSS 피드 기반 뉴스 데이터 수집
- 실시간 데이터 스트리밍
- Kafka 토픽으로 데이터 발행

### 2. 데이터 처리 (Consumer)
- Kafka 토픽 구독
- 뉴스 데이터 전처리
- 전문용어 처리 및 정규화
- Elasticsearch 인덱싱

### 3. 배치 처리 (Batch)
- Airflow를 통한 워크플로우 관리
- Spark를 활용한 대규모 데이터 처리
- 주기적인 데이터 분석 및 집계
- 리포트 생성

## 데이터 파이프라인 흐름

1. 데이터 수집
   ```
   RSS 피드 → Producer → Kafka 토픽
   ```

2. 데이터 처리
   ```
   Kafka 토픽 → Consumer → 전처리 → Elasticsearch
   ```

3. 배치 처리
   ```
   Airflow DAG → Spark Job → 분석 결과 저장
   ```

## 개발 가이드

### 프로듀서 개발
1. `producer/requirements.txt`에 의존성 추가
2. `rss_producer.py` 수정
3. 도커 이미지 재빌드

### 컨슈머 개발
1. `consumer/requirements.txt`에 의존성 추가
2. `rss_combined_consumer.py` 또는 `preprocess.py` 수정
3. 도커 이미지 재빌드

### 배치 작업 개발
1. `batch/dags/` 디렉토리에 새로운 DAG 파일 추가
2. Airflow UI에서 DAG 활성화
3. 필요한 경우 Spark 작업 추가

## 모니터링

### Kafka 모니터링
- Kafka Manager UI: `http://localhost:9000`
- 토픽 모니터링
- 컨슈머 그룹 모니터링

### Airflow 모니터링
- Airflow UI: `http://localhost:8080`
- DAG 실행 상태 확인
- 태스크 로그 확인

### Spark 모니터링
- Spark UI: `http://localhost:4040`
- 작업 실행 상태 확인
- 리소스 사용량 모니터링

## 환경 변수

### 프로듀서
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka 브로커 주소
- `KAFKA_TOPIC`: 발행할 토픽 이름
- `RSS_FEED_URLS`: 수집할 RSS 피드 URL 목록

### 컨슈머
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka 브로커 주소
- `KAFKA_TOPIC`: 구독할 토픽 이름
- `ELASTICSEARCH_URL`: Elasticsearch 서버 주소

### 배치
- `AIRFLOW_HOME`: Airflow 홈 디렉토리
- `SPARK_MASTER`: Spark 마스터 주소
- `ELASTICSEARCH_URL`: Elasticsearch 서버 주소

## 문제 해결

### 일반적인 문제
1. Kafka 연결 실패
   - Zookeeper 실행 상태 확인
   - Kafka 브로커 주소 확인
   - 네트워크 연결 확인

2. 컨슈머 처리 지연
   - 파티션 수 확인
   - 컨슈머 그룹 설정 확인
   - 리소스 사용량 모니터링

3. 배치 작업 실패
   - Airflow 로그 확인
   - Spark 로그 확인
   - 의존성 서비스 상태 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
