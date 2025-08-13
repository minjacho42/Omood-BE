from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import uuid4

class Session(BaseModel):
    id: str = Field(default=None, alias="_id", exclude=True)
    user_id: str
    subject: str
    goal: str
    duration: int
    break_duration: int
    tags: Optional[List[str]] = None
    started_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Literal["pending", "started", "paused", "completed", "reviewed"]
    reflection: Optional[str] = None
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }

class SessionResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    goal: str
    duration: int
    break_duration: int
    tags: Optional[List[str]] = None
    started_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Literal["pending", "started", "paused", "completed", "reviewed"]
    reflection: Optional[str] = None

class ReflectionUpdate(BaseModel):
    reflection: str