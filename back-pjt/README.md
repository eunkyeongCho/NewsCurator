# 뉴스 데이터 분석 백엔드 서버

Django 기반의 뉴스 데이터 분석 및 처리 백엔드 서버입니다. RESTful API를 제공하며, 뉴스 데이터의 수집, 분석, 저장 및 챗봇 기능을 지원합니다.

## 기술 스택

- Python 3.10
- Django 4.2.11
- Django REST Framework 3.15.1
- PostgreSQL
- Elasticsearch 8.12.1
- LangChain (챗봇)
- scikit-learn 1.3.2 (데이터 분석)
- pandas 2.2.3 (데이터 처리)

## 프로젝트 구조

```
back-pjt/
├── accounts/                # 사용자 인증 관련 앱
├── news/                    # 뉴스 데이터 처리 앱
│   ├── models.py           # 데이터 모델
│   ├── views.py            # API 엔드포인트
│   ├── serializers.py      # 데이터 직렬화
│   ├── urls.py             # URL 라우팅
│   ├── utils.py            # 유틸리티 함수
│   └── chatbot/            # 챗봇 관련 기능
├── config/                 # 프로젝트 설정
├── manage.py               # Django 관리 스크립트
├── requirements.txt        # Python 패키지 의존성
└── Dockerfile             # 도커 설정
```

## 시작하기

### 로컬 개발 환경 설정

1. Python 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env
# .env 파일을 편집하여 필요한 환경 변수 설정
```

4. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

5. 개발 서버 실행
```bash
python manage.py runserver
```

### Docker를 사용한 실행

1. 도커 이미지 빌드
```bash
docker build -t news-backend .
```

2. 도커 컨테이너 실행
```bash
docker run -p 8000:8000 news-backend
```

## API 엔드포인트

### 인증
- `POST /api/auth/login/` - 로그인
- `POST /api/auth/logout/` - 로그아웃
- `POST /api/auth/register/` - 회원가입

### 뉴스
- `GET /api/news/` - 뉴스 목록 조회
- `GET /api/news/{id}/` - 뉴스 상세 조회
- `GET /api/news/trending/` - 트렌딩 뉴스 조회
- `GET /api/news/search/` - 뉴스 검색

### 챗봇
- `POST /api/chatbot/` - 챗봇 대화

## 주요 기능

1. 뉴스 데이터 관리
   - 뉴스 데이터 수집 및 저장
   - 뉴스 검색 및 필터링
   - 트렌딩 뉴스 분석

2. 사용자 관리
   - JWT 기반 인증
   - 사용자 프로필 관리
   - 권한 관리

3. 데이터 분석
   - 뉴스 데이터 분석
   - 트렌드 분석
   - 키워드 추출

4. 챗봇
   - LangChain 기반 챗봇
   - 뉴스 관련 질의응답
   - 자연어 처리

## 개발 가이드

### 코드 스타일
- PEP 8 스타일 가이드 준수
- Django 코딩 스타일 가이드 준수

### 테스트
```bash
python manage.py test
```

### 마이그레이션
```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate
```

## 배포

### Docker 배포
1. 도커 이미지 빌드
```bash
docker build -t news-backend:latest .
```

2. 도커 컨테이너 실행
```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name news-backend \
  news-backend:latest
```

### 환경 변수
필요한 환경 변수:
- `SECRET_KEY`: Django 시크릿 키
- `DEBUG`: 디버그 모드 (True/False)
- `DATABASE_URL`: 데이터베이스 연결 URL
- `ELASTICSEARCH_URL`: Elasticsearch 연결 URL
- `OPENAI_API_KEY`: OpenAI API 키 (챗봇용)

## 모니터링

- Django Health Check: `/health/`
- Django Admin: `/admin/`

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 