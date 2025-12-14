FROM docker.elastic.co/elasticsearch/elasticsearch:8.9.0

# nori 플러그인 설치
RUN elasticsearch-plugin install analysis-nori

# 매핑 파일과 초기화 스크립트 복사
COPY mappings /usr/share/elasticsearch/mappings
COPY --chmod=755 init/init-mappings.sh /usr/local/bin/init-mappings.sh

# 초기화 스크립트를 실행하도록 설정
CMD ["/bin/bash", "-c", "/usr/local/bin/init-mappings.sh & /usr/local/bin/docker-entrypoint.sh"] 