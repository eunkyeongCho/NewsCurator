FROM python:3.10

# 프록시 설정 완전 비활성화
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV http_proxy=""
ENV https_proxy=""
ENV no_proxy="*"
ENV PIP_NO_PROXY="*"

# Java 설치
RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
COPY apache_flink-2.0.0-cp310-cp310-manylinux1_x86_64.whl ./
COPY jargroup/ ./jargroup/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir apache_flink-2.0.0-cp310-cp310-manylinux1_x86_64.whl
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "-u", "rss_combined_consumer.py"]