#!/bin/bash
set -e

echo "=== entrypoint.sh 진입 ==="
# 1. Kafka가 준비될 때까지 대기
/app/wait-for-it.sh kafka:9092 -t 60

# 2. 토픽 생성 (이미 있으면 무시됨)
# kafka-topics.sh가 producer 컨테이너에 없으므로, kafka 컨테이너에서 실행
echo "=== wait-for-it.sh 종료 ==="
# docker exec kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic article --partitions 1 --replication-factor 1 || true

# 3. producer 실행
echo "=== producer 실행 ==="
python3 -u rss_producer.py

echo "=== python3 명령 종료 ==="
