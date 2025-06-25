from sqlalchemy import Column, String, UniqueConstraint
from .base import Base
from pydantic import BaseModel
from typing import Optional

# SQLAlchemy 모델 (DB용)
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Google user id
    provider = Column(String, nullable=False)
    provider_id = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="uq_provider_provider_id"),
    )


# Pydantic 모델 (응답용)
class UserResponse(BaseModel):
    id: str
    provider: str
    provider_id: str
    email: str
    name: Optional[str]
    picture: Optional[str]

    class Config:
        from_attributes = True