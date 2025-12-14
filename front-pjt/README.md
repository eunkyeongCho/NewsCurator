# 뉴스 데이터 시각화 프론트엔드

Vue.js 기반의 뉴스 데이터 시각화 웹 애플리케이션입니다. 실시간 뉴스 데이터를 시각적으로 표현하고, 사용자 친화적인 인터페이스를 제공합니다.

## 기술 스택

### 핵심 프레임워크
- Vue.js 3.5
- Vite 5.4
- Vue Router 4.4
- Pinia 3.0 (상태 관리)

### UI/UX
- Chart.js 4.4 (데이터 시각화)
- Vue Chart.js 5.3
- SASS (스타일링)

### 개발 도구
- Vite DevTools
- Vue DevTools
- Vitest (테스트)

## 프로젝트 구조

```
front-pjt/
├── src/                      # 소스 코드
│   ├── assets/              # 정적 자원 (이미지, 스타일 등)
│   ├── components/          # 재사용 가능한 컴포넌트
│   │   ├── icon/           # 아이콘 컴포넌트
│   │   ├── ArticleChatbot.vue    # 뉴스 기사 챗봇 컴포넌트
│   │   ├── ArticlePreview.vue    # 뉴스 기사 미리보기
│   │   ├── BoardCard.vue         # 게시판 카드 컴포넌트
│   │   ├── CommentBox.vue        # 댓글 입력 컴포넌트
│   │   ├── NewsCard.vue          # 뉴스 카드 컴포넌트
│   │   ├── SearchBar.vue         # 검색바 컴포넌트
│   │   ├── TheFooter.vue         # 푸터 컴포넌트
│   │   └── TheHeader.vue         # 헤더 컴포넌트
│   │
│   ├── views/               # 페이지 컴포넌트
│   │   ├── BookmarkListView.vue  # 북마크 목록 페이지
│   │   ├── DashBoardView.vue     # 대시보드 페이지
│   │   ├── LoginPage.vue         # 로그인 페이지
│   │   ├── NewsDetailView.vue    # 뉴스 상세 페이지
│   │   ├── NewsView.vue          # 뉴스 목록 페이지
│   │   ├── NotFoundView.vue      # 404 페이지
│   │   └── SignUp.vue            # 회원가입 페이지
│   │
│   ├── composables/         # Vue 컴포지션 API 관련 로직
│   ├── router/              # 라우팅 설정
│   ├── common/              # 공통 유틸리티
│   ├── App.vue              # 루트 컴포넌트
│   ├── main.js              # 진입점
│   └── axios.js             # API 통신 설정
│
├── public/                  # 정적 파일
├── index.html              # HTML 템플릿
├── vite.config.js          # Vite 설정
├── jsconfig.json           # JavaScript 설정
├── package.json            # 의존성 관리
└── Dockerfile              # 도커 설정
```

### 컴포넌트 설명

#### 공통 컴포넌트
- `TheHeader.vue`: 네비게이션 바와 검색 기능을 포함한 헤더
- `TheFooter.vue`: 저작권 정보와 링크를 포함한 푸터
- `SearchBar.vue`: 뉴스 검색 기능을 제공하는 검색바

#### 뉴스 관련 컴포넌트
- `NewsCard.vue`: 뉴스 기사의 요약 정보를 카드 형태로 표시
- `ArticlePreview.vue`: 뉴스 기사의 미리보기 제공
- `ArticleChatbot.vue`: 뉴스 기사에 대한 챗봇 인터페이스
- `BoardCard.vue`: 게시판 형태의 뉴스 목록 표시
- `CommentBox.vue`: 뉴스 기사에 대한 댓글 기능

### 페이지 설명

#### 인증 관련 페이지
- `LoginPage.vue`: 사용자 로그인
- `SignUp.vue`: 새로운 사용자 회원가입

#### 뉴스 관련 페이지
- `NewsView.vue`: 뉴스 목록 및 필터링
- `NewsDetailView.vue`: 뉴스 기사 상세 내용
- `BookmarkListView.vue`: 사용자의 북마크된 뉴스 목록

#### 대시보드
- `DashBoardView.vue`: 뉴스 트렌드, 키워드 분석 등 데이터 시각화

#### 기타
- `NotFoundView.vue`: 404 에러 페이지

## 시작하기

### 사전 요구사항
- Node.js 18.0 이상
- npm 9.0 이상

### 로컬 개발 환경 설정

1. 의존성 설치
```bash
npm install
```

2. 개발 서버 실행
```bash
npm run dev
```

3. 프로덕션 빌드
```bash
npm run build
```

4. 프로덕션 빌드 미리보기
```bash
npm run serve
```

### Docker를 사용한 실행

1. 도커 이미지 빌드
```bash
docker build -t news-frontend .
```

2. 도커 컨테이너 실행
```bash
docker run -p 5173:5173 news-frontend
```

## 주요 기능

### 1. 뉴스 데이터 시각화
- 실시간 뉴스 트렌드 차트
- 키워드 분석 그래프
- 카테고리별 뉴스 분포
- 시계열 데이터 시각화

### 2. 사용자 인터페이스
- 반응형 웹 디자인
- 다크/라이트 모드
- 직관적인 네비게이션
- 실시간 데이터 업데이트

### 3. 데이터 관리
- 실시간 데이터 동기화
- 로컬 상태 관리 (Pinia)
- API 통신 (Axios)
- 에러 처리

## 개발 가이드

### 컴포넌트 개발
1. `src/components/` 디렉토리에 새 컴포넌트 생성
2. Vue 컴포넌트 작성
3. 필요한 경우 스타일 추가 (SASS)
4. 컴포넌트 등록 및 사용

### 페이지 개발
1. `src/views/` 디렉토리에 새 페이지 생성
2. `src/router/`에 라우트 추가
3. 필요한 컴포넌트 import 및 사용
4. 페이지별 스타일 정의

### 상태 관리
1. Pinia 스토어 생성
2. 상태 및 액션 정의
3. 컴포넌트에서 스토어 사용
4. 필요한 경우 지속성 설정

## 환경 변수

`.env` 파일을 통해 다음 환경 변수 설정:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## 빌드 및 배포

### 프로덕션 빌드
```bash
npm run build
```
- `dist/` 디렉토리에 최적화된 빌드 파일 생성
- 자동 코드 분할
- 정적 자원 최적화

### 정적 호스팅
- Nginx 설정 예시
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 테스트

### 단위 테스트
```bash
npm run test
```

### 테스트 커버리지
```bash
npm run test:coverage
```

## 성능 최적화

1. 코드 분할
   - 동적 import 사용
   - 라우트 기반 코드 분할

2. 캐싱 전략
   - 정적 자원 캐싱
   - API 응답 캐싱

3. 이미지 최적화
   - WebP 포맷 사용
   - 지연 로딩 적용

## 문제 해결

### 일반적인 문제
1. 개발 서버 연결 실패
   - 포트 충돌 확인
   - 방화벽 설정 확인

2. 빌드 실패
   - Node.js 버전 확인
   - 의존성 충돌 확인
   - 캐시 삭제 후 재시도

3. API 통신 오류
   - CORS 설정 확인
   - API 엔드포인트 확인
   - 네트워크 연결 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
