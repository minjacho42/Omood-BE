from datetime import datetime, timedelta
import jwt
from app.core.config import settings
from fastapi import Cookie, HTTPException
from typing import Optional
from jwt.exceptions import PyJWTError
from app.utils.logging import logger

logger = logger.bind(layer="service", module="auth")

async def get_authenticated_user_id(omood_at: Optional[str] = Cookie(None)) -> str:
    if omood_at is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(omood_at, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_access_token(user_id: str, expires_delta: timedelta = timedelta(hours=1)):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + expires_delta,
    }
    logger.bind(event="create_access_token").info(payload)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
