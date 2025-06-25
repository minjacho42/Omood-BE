from sqlalchemy.ext.asyncio import AsyncSession
from app.services.google_api.auth import get_token_with_code as google_auth_token
from app.services.google_api.user import get_user_with_token as google_user
from app.models.user import User
from app.repositories.user import update_user, get_user_by_id
from fastapi import HTTPException

async def create_or_update_user(provider: str, provider_code: str, db: AsyncSession) -> User:
    if provider == "google":
        token_dict = google_auth_token(provider_code)
        user = google_user(token_dict["access_token"])
    else:
        raise HTTPException(status_code=401, detail="Invalid provider code")
    user = await update_user(user, db)
    return user

async def get_user_info(user_id: str, db: AsyncSession):
    return await get_user_by_id(user_id, db)