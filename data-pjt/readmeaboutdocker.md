## `docker-compose up -d` 명령어 하나로 모든 것이 자동으로 설정

1. PostgreSQL:
   - vector 확장 설치 (Dockerfile)
   - postgres 역할 생성 (`01-init-user.sql`)
   - vector 확장 활성화 (`02-init-vector.sql`)
   - 데이터 백업 복원 (`03-news_backup.sql`)

2. Elasticsearch:
   - nori 플러그인 설치 (Dockerfile)
   - 서비스 시작 후 자동으로 매핑 적용 (`init-mappings.sh`)

3. 실행 순서:
   ```
   1. PostgreSQL 컨테이너 시작
      ↓
   2. 초기화 스크립트 순차 실행 (01 → 02 → 03)
      ↓
   3. Elasticsearch 컨테이너 시작
      ↓
   4. nori 플러그인 로드
      ↓
   5. 서비스 준비되면 매핑 자동 적용
      ↓
   6. Kibana 시작
   ```

모든 설정이 자동화되어 있어서, 다음에 시스템을 재배포하거나 다른 환경에서 실행할 때도 동일한 환경을 쉽게 구성할 수 있습니다.
