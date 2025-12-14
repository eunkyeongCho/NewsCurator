#!/bin/bash
cd data-pjt/docker
set -e

echo "Airflow DB 초기화"
docker-compose run --rm report airflow db init


echo "1. DB(Postgres) 및 백엔드 시작..."
docker-compose up -d postgres
# Postgres가 healthy 상태가 될 때까지 대기
echo "   - Postgres 준비 대기..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' postgres)" == "healthy" ]; do
  sleep 2
  echo -n "."
done
echo "   - Postgres 준비 완료!"

docker-compose up -d back

echo "2. HDFS 시작..."
docker-compose up -d namenode datanode

echo "3. Kafka, Zookeeper 시작..."
docker-compose up -d zookeeper kafka
# Kafka가 포트 열릴 때까지 대기
echo "   - Kafka 준비 대기..."
until docker exec kafka bash -c "nc -z localhost 9092"; do
  sleep 2
  echo -n "."
done
echo "   - Kafka 준비 완료!"

echo "4. Flink 시작..."
docker-compose up -d jobmanager taskmanager

echo "5. Elasticsearch 시작..."
docker-compose up -d elasticsearch

echo "6. Producer/Consumer 시작..."
docker-compose up -d producer
docker-compose up -d consumer

echo "7. Spark 클러스터 시작..."
docker-compose up -d spark-master spark-worker

echo "8. Airflow Report 서비스 시작..."
docker-compose up -d report
docker exec -it docker-report-1 airflow connections delete spark_default && docker exec -it docker-report-1 airflow connections add 'spark_default' --conn-type 'spark' --conn-host 'spark://spark-master' --conn-port '7077' --conn-extra '{"deploy-mode": "client", "master": "spark://spark-master:7077"}'

echo "모든 서비스가 순차적으로 시작되었습니다!"

echo "9. 뉴스 큐레이터 서비스를 시작합니다"
docker-compose up front

