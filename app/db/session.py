from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite를 위한 연결 URL
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL  # 로컬 파일로 저장됨

# DB 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 세션 로컬 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)