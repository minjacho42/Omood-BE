from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import uuid4

class MemoAttachment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal["image", "audio"]
    key: str
    filename: str

class Memo(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id", exclude=True)
    user_id: str
    content: str
    tags: Optional[List[str]] = None
    attachments: Optional[List[MemoAttachment]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    category: Optional[str] = None
    category_confidence: Optional[float] = None
    is_archived: Optional[bool] = False
    # last_viewed_at: Optional[datetime]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }

class MemoAttachmentResponse(BaseModel):
    id: str
    type: Literal["image", "audio"]
    url: str
    filename: str

class MemoResponse(BaseModel):
    id: str
    user_id: str
    content: str
    tags: Optional[List[str]]
    attachments: Optional[List[MemoAttachmentResponse]] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    category_confidence: Optional[float] = None
    is_archived: Optional[bool] = False
    # last_viewed_at: Optional[datetime]