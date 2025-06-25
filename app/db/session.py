from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

# Async DB URL
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# Async 엔진 생성
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
)

# Async 세션 로컬 생성기
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 초기 테이블 생성용 함수
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)