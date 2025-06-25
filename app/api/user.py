from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.models.user import UserResponse
from app.services.auth import get_authenticated_user_id
from app.services.user import get_user_info

router = APIRouter()

@router.get("/me", response_model=UserResponse, name="me", summary="Get current user info")
async def get_me(user_id: str = Depends(get_authenticated_user_id), db = Depends(get_db)):
    general_user = await get_user_info(user_id, db)
    return general_user