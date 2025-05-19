# backend/app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import auth, user
from app.core.config import settings
from app.db.session import engine
from app.models.user import Base
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 실행
    Base.metadata.create_all(bind=engine)
    yield
    # 앱 종료 시 실행할 코드가 있다면 여기에 추가
    # 예: 세션 정리, 로그 저장 등
    # await db_cleanup()
app = FastAPI(
    title="Omood API",
    description="Spotify 기반 오늘의 Mood 인사이트 API",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS (프론트-백엔드 분리 배포시 필요)
origins = [
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 (엔드포인트 기능별 분리)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])

# 기본 헬스체크 엔드포인트
@app.get("/", tags=["health"])
def health_check():
    return {"msg": "Omood API running!"}
