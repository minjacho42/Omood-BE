from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    country = Column(String, nullable=True)
    product = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)


class UserResponse(BaseModel):
    id: str
    display_name: Optional[str]
    email: Optional[str]
    country: Optional[str]
    product: Optional[str]
    profile_image_url: Optional[str]

    class Config:
        from_attributes = True