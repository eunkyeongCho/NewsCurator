#!/bin/bash

# Spark 연결 삭제 (에러 무시)
airflow connections delete spark_default || true

# Spark 연결 추가 (standalone 모드)
airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark://spark-master' \
    --conn-port '7077' \
    --conn-extra '{"deploy-mode": "client", "master": "spark://spark-master:7077", "queue": null, "yarn.enabled": false}'

# Standalone 모드로 Airflow 실행
airflow standalone 