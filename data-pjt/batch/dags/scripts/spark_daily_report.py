import sys
import argparse
import os
import shutil
import json
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, from_json, to_timestamp, date_format, count
from pyspark.sql.types import StructType, ArrayType, StringType, TimestampType
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def main(report_date_str):
    print(f"시작 날짜: {report_date_str}")
    
    # 설정
    FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    INPUT_PATH = "hdfs://namenode:9000/user/hadoop/articles.json"
    ARCHIVE_DIR = "/opt/airflow/dags/data/news_archive"
    REPORT_DIR = "/opt/airflow/dags/data"
    # ARCHIVE_DIR = "/mnt/c/Users/SSAFY/Desktop/PJT/data-pjt/batch/dags/data/news_archive"
    # REPORT_DIR = "/mnt/c/Users/SSAFY/Desktop/PJT/data-pjt/batch/dags/data"

    spark = SparkSession.builder \
            .appName("DailyNewsReport") \
            .getOrCreate()

    # 스키마 정의
    schema = StructType() \
        .add("write_date", StringType()) \
        .add("keywords", ArrayType(StringType()))
    
    # 데이터 로드
    df = spark.read.schema(schema).json(INPUT_PATH)
    # 날짜 변환
    df = df.withColumn("write_date", to_timestamp("write_date"))
    
    # 기준 날짜 필터
    report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
    next_day = report_date + timedelta(days=1)

    df_filtered = df.filter((col("write_date") >= report_date) & (col("write_date") < next_day))
    # 키워드 explode 및 집계
    keyword_df = df_filtered.select(explode(col("keywords")).alias("keyword")) \
                            .groupBy("keyword") \
                            .agg(count("*").alias("count")) \
                            .orderBy(col("count").desc()) \
                            .limit(10)

    # 결과 수집
    top_keywords = keyword_df.collect()

    if not top_keywords:
        print("해당 날짜의 데이터가 없습니다.")
        return

    keywords = [row['keyword'] for row in top_keywords]
    counts = [row['count'] for row in top_keywords]
    # 시각화
    plt.rcParams["font.family"] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(10, 6))
    plt.bar(keywords, counts)
    plt.xlabel('빈도수')
    plt.title(f'{report_date_str} 키워드 TOP10')
    plt.tight_layout()

    # PDF 저장
    report_file = os.path.join(REPORT_DIR, f"report_{report_date_str}.pdf")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)  # 디렉토리가 없으면 생성
    plt.savefig(report_file)
    print(f"리포트 저장 완료: {report_file}")

    # 데이터 백업
    archive_path = os.path.join(ARCHIVE_DIR, f"data_{report_date_str}.json")
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)  # 디렉토리가 없으면 생성
    pdf = df_filtered.toPandas()
    pdf.to_json(archive_path, orient='records', force_ascii=False, lines=False)
    print(f"원본 데이터 이동 완료: {archive_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark를 이용한 일일 뉴스 리포트 생성")
    parser.add_argument("--date", required=True, help="보고서 기준 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()

    main(args.date)
    # main("2025-05-01")
