from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Snippet(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id", exclude=True)
    user_id: str
    content_type: str # "text", "image", or "audio"
    content: Optional[str] = None
    content_key: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }

class SnippetResponse(BaseModel):
    id: str
    user_id: str
    content_type: str
    content: Optional[str] = None
    content_url: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)