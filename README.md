<p align="center">
  <img src="src/omood.svg" alt="Omood Logo" width="120" />
</p>
<h1 align="center"><b>Omood</b> <span>🎧</span></h1>
<p align="center"><i>음악과 무(무드)를 결합한, 나만의 감정 음악 대시보드</i></p>

**Omood**는 Spotify 소셜 로그인을 통해 사용자의 음악 재생 기록을 수집하고, 시간대 및 요일별로 분석하여 시각화하는 개인 맞춤형 음악 소비 인사이트 대시보드입니다.

---

## 📌 주요 기능

### ✅ MVP
- Spotify OAuth 2.0 기반 소셜 로그인
- `/v1/me/player/recently-played` API로 재생 기록 수집
- 시간대별 / 요일별 음악 청취 패턴 시각화

### 🔄 추후 확장 가능성
- 감정 기반 음악 추천 (valence, energy 분석)
- 기분 예측 및 플레이리스트 자동 생성
- MLOps 기반 학습 및 추천 자동화

---

## 🗂️ 디렉토리 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 앱 시작점
│   ├── api/                # 라우터(엔드포인트) 모음
│   │   ├── __init__.py
│   │   ├── auth.py         # 인증 관련 (Spotify OAuth)
│   │   ├── tracks.py       # 음악/재생 기록 관련 API
│   │   └── user.py         # 사용자 정보 관련 API
│   ├── core/               # 핵심 설정, 유틸, 공통 기능
│   │   ├── __init__.py
│   │   ├── config.py       # 환경변수, 세팅 관리
│   │   └── scheduler.py    # APScheduler 등 주기 작업
│   ├── db/                 # DB, 모델, CRUD 분리
│   │   ├── __init__.py
│   │   ├── base.py         # DB 세션/기초 설정
│   │   └── models.py       # ORM 모델
│   ├── services/           # 비즈니스 로직 (크롤링, 분석 등)
│   │   ├── __init__.py
│   │   ├── crawl.py        # Spotify 기록 크롤러
│   │   ├── spotify_api.py  # Spotify API
│   │   ├── spotify_token.py# Spotify token 관리
│   │   └── mood.py         # 감정 분석 등
│   └── utils/              # 유틸 함수 (공통 함수/도우미)
│       ├── __init__.py
│       └── logging.py      # logger용 파일
├── tests/                  # 테스트 코드
│   └── test_api.py
├── requirements.txt
├── .env
└── README.md
```

---

## 🚀 실행 방법

### 🔐 .env 설정

**백엔드 (`.env`)**
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
REDIRECT_URI=
```

### ✅ 실행 명령어

```bash
# 백엔드
cd backend
uvicorn main:app --reload
```

---

## 🧠 기획 의도

- 매일 듣는 음악을 통해 나만의 **기분 기록 일지**를 만들 수 없을까?
- 음악 소비 패턴을 통해 **자기 인식(self-awareness)**을 돕고, 나아가 **개인화된 추천**까지 연결되는 서비스를 지향합니다.

---

## 🛡️ 주의사항

- 본 프로젝트는 Spotify API 정책을 준수하며, 비상업적 사이드 프로젝트 목적입니다.