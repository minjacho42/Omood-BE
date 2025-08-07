🧠 프로젝트 개요: Omood – 하루 메모 요약 및 자동 정리 시스템

Omood는 사용자가 하루 동안 기록한 텍스트, 이미지, 음성 메모를 저장하고, 이를 AI 기반으로 자동 요약 및 키워드 정리하여 제공하는 개인 맞춤형 회고 메모 대시보드입니다.

단순 저장을 넘어서, 인공지능 요약, 검색, 분석을 통해 일상을 돌아보는 경험을 제공합니다.

⸻

📌 주요 기능

✅ MVP
	•	텍스트/이미지/음성 메모 저장 (FastAPI)
	•	AI 기반 하루 요약 및 키워드 추출 (OpenAI API)
	•	Elasticsearch 기반 메모 검색
	•	웹훅 또는 email을 통한 요약 결과 알림

⸻

API Endpoint

Method	Path	Description
POST	/api/auth/google/login	구글 소셜 로그인
POST	/api/auth/apple/login	애플 소셜 로그인
POST	/api/auth/refresh	토큰 재발급
GET	/api/user/me	내 정보 조회
PUT	/api/user/me	내 정보 수정
POST	/api/memo	메모 생성
GET	/api/memo	월별 메모 조회
GET	/api/memo/{memo_id}	특정 메모 조회
PUT	/api/memo/{memo_id}	메모 수정
DELETE	/api/memo/{memo_id}	메모 삭제


⸻

Code Structure

API (app/api)
	•	auth.py: 인증 관련 API (로그인, 토큰 재발급)
	•	memo.py: 메모 관련 CRUD API
	•	user.py: 유저 정보 관련 API

Service (app/services)
	•	auth.py: 인증 비즈니스 로직
	•	memo.py: 메모 분석, 요약, 알림 전송 로직
	•	user.py: 유저 관련 비즈니스 로직

Repository (app/repositories)
	•	memo.py: 메모 DB CRUD
	•	user.py: 유저 DB CRUD
	•	s3.py: 이미지/음성 파일 저장 처리

⸻

🔄 확장 가능성
	•	유사 메모 추천 기능 (vector search 기반)
	•	GPT 기반 문맥 연결 보강 및 리마인드 기능
	•	분석 결과 Notion/Email 연동 등 알림 채널 다양화

⸻

🗂️ 디렉토리 구조

backend/
├── app/
│   ├── main.py             # FastAPI 앱 진입점
│   ├── api/                # 엔드포인트 라우터
│   ├── core/               # 설정, 유틸, 스케줄러
│   ├── db/                 # DB 설정 및 ORM 모델
│   ├── services/           # 메모 요약, 알림, 처리 로직
│   └── utils/              # 공통 유틸 함수
├── tests/                  # 테스트 코드
├── requirements.txt
├── .env
└── README.md


⸻

🚀 실행 방법

🔐 .env 설정 예시

OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

✅ 실행 명령어

# 백엔드 실행
cd backend
uvicorn main:app --reload


⸻

🧠 기획 의도
	•	하루 동안의 단상, 아이디어, 일상 기록을 부담 없이 메모하고
	•	AI를 통해 자동 정리된 요약과 키워드로 스스로를 되돌아보는 경험을 제공합니다.

⸻

🛡️ 주의사항
	•	본 프로젝트는 비상업적 사이드 프로젝트이며, 모든 데이터는 사용자 단위로 분리 저장됩니다.