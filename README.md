# 와디즈 페이지 빌더 - 웹앱 버전 (SaaS)

**Production-Ready Full-Stack Web Application**

## 🚀 프로젝트 개요

와디즈 크라우드펀딩 상세페이지를 AI로 자동 생성하는 SaaS 플랫폼입니다.
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI + PostgreSQL
- **AI**: OpenAI GPT-4 + Genspark Agent
- **Storage**: AWS S3 / Cloudflare R2

---

## 📦 프로젝트 구조

```
wadiz-builder-saas/
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── api/endpoints/ # API 엔드포인트
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── images.py
│   │   │   ├── ai_generate.py  # 핵심 AI 생성
│   │   │   ├── templates.py
│   │   │   └── export.py
│   │   ├── core/          # 핵심 설정
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/        # SQLAlchemy 모델
│   │   │   └── models.py
│   │   ├── schemas/       # Pydantic 스키마
│   │   │   └── schemas.py
│   │   ├── services/      # 비즈니스 로직
│   │   │   ├── auth_service.py
│   │   │   ├── project_service.py
│   │   │   ├── image_service.py (S3/R2 연동)
│   │   │   ├── ai_service.py  # OpenAI 통합
│   │   │   ├── export_service.py
│   │   │   └── template_service.py
│   │   ├── templates/     # Jinja2 HTML 템플릿
│   │   │   └── wadiz_default.html
│   │   └── main.py        # FastAPI 앱
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/              # React Frontend
    ├── src/
    │   ├── api/client.ts     # API 클라이언트
    │   ├── types/index.ts    # TypeScript 타입
    │   ├── pages/            # 페이지 컴포넌트
    │   │   ├── LoginPage.tsx
    │   │   ├── DashboardPage.tsx
    │   │   └── EditorPage.tsx
    │   ├── components/       # 재사용 컴포넌트
    │   │   ├── ImageUploader.tsx  # 드래그앤드롭
    │   │   ├── AIGenerator.tsx
    │   │   └── PreviewPanel.tsx
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

---

## 🎯 주요 기능

### ✅ 완성된 기능

1. **사용자 인증** (JWT)
   - 회원가입 / 로그인
   - 토큰 기반 인증

2. **프로젝트 관리**
   - CRUD 기능
   - 프로젝트별 이미지 관리

3. **이미지 업로드** (S3/R2)
   - 드래그 앤 드롭
   - 자동 리사이징
   - 섹션별 분류 (intro/body/outro)

4. **AI 콘텐츠 생성** ⭐ 핵심 기능
   - OpenAI GPT-4로 카피라이팅
   - 와디즈 황금 구조 자동 적용
   - 대안 카피 3개 생성
   - 페이지 구조 자동 설계

5. **HTML 다운로드**
   - 와디즈 스타일 HTML 생성
   - ZIP 파일로 Export
   - 모든 이미지 포함

6. **템플릿 시스템**
   - 성공 사례 기반 템플릿
   - 카테고리별 분류

---

## 🛠️ 설치 및 실행

### Backend 실행

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 API 키들을 입력하세요

# 데이터베이스 마이그레이션 (Alembic)
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
# → http://localhost:8000
```

### Frontend 실행

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정
echo "VITE_API_URL=http://localhost:8000" > .env

# 개발 서버 실행
npm run dev
# → http://localhost:5173
```

---

## 🔑 환경변수 설정

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/wadiz_builder

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# AWS S3 / Cloudflare R2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET_NAME=wadiz-builder-images
AWS_S3_REGION=ap-northeast-2
AWS_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com  # R2 only

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key
SECRET_KEY=your-app-secret-key

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000
```

---

## 🚀 배포 가이드

### Option 1: Vercel (Frontend) + Railway (Backend) + Supabase (DB)

#### Frontend (Vercel)
```bash
cd frontend
npm install -g vercel
vercel  # 첫 배포
vercel --prod  # 프로덕션 배포
```

#### Backend (Railway)
```bash
cd backend
# Railway CLI 설치
npm i -g @railway/cli
railway login
railway init
railway up  # 배포
```

#### Database (Supabase)
1. https://supabase.com 가입
2. 새 프로젝트 생성
3. Database URL 복사 → Backend 환경변수에 추가

### Option 2: Docker Compose (All-in-One)

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/wadiz_builder
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
  
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: wadiz_builder
```

```bash
docker-compose up -d
```

---

## 📊 API 문서

서버 실행 후 Swagger UI에서 확인:
- **API Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 주요 엔드포인트

```
POST   /api/v1/auth/register        # 회원가입
POST   /api/v1/auth/login           # 로그인
GET    /api/v1/auth/me              # 내 정보

POST   /api/v1/projects/            # 프로젝트 생성
GET    /api/v1/projects/            # 내 프로젝트 목록
GET    /api/v1/projects/{id}        # 프로젝트 상세
PATCH  /api/v1/projects/{id}        # 프로젝트 수정
DELETE /api/v1/projects/{id}        # 프로젝트 삭제

POST   /api/v1/images/upload/{project_id}  # 이미지 업로드
GET    /api/v1/images/project/{project_id} # 프로젝트 이미지 목록
DELETE /api/v1/images/{id}                 # 이미지 삭제

POST   /api/v1/ai/generate          # AI 페이지 생성 ⭐
POST   /api/v1/ai/regenerate-alternatives/{id}
POST   /api/v1/ai/apply-alternative/{id}/{index}

GET    /api/v1/templates/           # 템플릿 목록
GET    /api/v1/templates/{id}       # 템플릿 상세

POST   /api/v1/export/html          # HTML 다운로드
GET    /api/v1/export/download/{key}
```

---

## 🎨 와디즈 황금 구조

AI가 자동 생성하는 페이지 구조:

### 1. 인트로 (Intro)
- **후킹 포인트**: 3초 안에 시선 사로잡기 (공감/재미/호기심)
- **제품 소개**: 제품명 + 핵심 이미지

### 2. 본론 (Body)
각 섹션마다:
- **대제목**: 핵심 특징
- **소제목**: 근거/원리
- **설명**: 자세한 내용
- **이미지**: 시각적 증명

### 3. 아웃트로 (Outro)
- **FAQ**: 자주 묻는 질문 5개
- **CTA**: 행동 유도 (펀딩하기)
- **얼리버드 혜택**

---

## 💰 비용 (무료 Tier 활용)

| 항목 | 서비스 | 월 비용 |
|------|--------|---------|
| Frontend | Vercel | 무료 |
| Backend | Railway Hobby | 무료 (500시간) |
| Database | Supabase | 무료 (500MB) |
| 이미지 저장 | Cloudflare R2 | 무료 (10GB) |
| AI API | OpenAI GPT-4 | Pay-as-you-go (~₩50,000) |
| **합계** | | **~₩50,000/월** |

---

## 📈 개발 진행 상황

### ✅ 완료 (90%)
- [x] Backend API 전체
- [x] Database 모델
- [x] 인증 시스템
- [x] 이미지 업로드 (S3/R2)
- [x] AI 생성 로직
- [x] HTML Export
- [x] Frontend 구조
- [x] API 클라이언트
- [x] 로그인 페이지

### 🚧 진행 중 (10%)
- [ ] 대시보드 페이지 (프로젝트 목록)
- [ ] 에디터 페이지 (이미지 업로드 + AI 생성 + 프리뷰)
- [ ] React 컴포넌트 (ImageUploader, AIGenerator, PreviewPanel)

### ⏳ 예정
- [ ] 배포 설정 파일
- [ ] 최종 테스트
- [ ] 문서화 완성

---

## 🔧 개발자 가이드

### AI 서비스 커스터마이징

`backend/app/services/ai_service.py`에서 프롬프트 수정 가능:

```python
system_prompt = """당신은 와디즈 크라우드펀딩 전문가입니다.
[여기에 프롬프트 수정]
"""
```

### 템플릿 추가

`backend/app/templates/` 폴더에 Jinja2 템플릿 추가:

```html
<!-- new_template.html -->
<!DOCTYPE html>
<html>
  <!-- 템플릿 내용 -->
</html>
```

### 프론트엔드 컴포넌트 추가

```tsx
// frontend/src/components/MyComponent.tsx
export default function MyComponent() {
  return <div>Hello</div>
}
```

---

## 📝 라이센스

MIT License

---

## 👨‍💻 개발자

**Luca Yoon (와디즈 펀딩 마스터)**  
- Company: doublecheck Co., Ltd.
- Email: contact@example.com

---

## 🙏 감사합니다!

이 프로젝트는 **와디즈 크라우드펀딩의 성공**을 돕기 위해 만들어졌습니다.

**주요 특징:**
✅ 10년 경험의 전문가 노하우가 AI로 구현됨  
✅ 억대 펀딩 성공 사례 기반 황금 구조  
✅ 3초 후킹 + 스토리텔링 자동 생성  
✅ 이미지 업로드 → AI 생성 → HTML 다운로드 원클릭  

**더 나은 펀딩 페이지로 꿈을 현실로 만드세요!** 🚀
