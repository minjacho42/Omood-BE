from fastapi import APIRouter, Depends
from app.models.user import UserResponse
from app.services.auth import get_authenticated_user_id
from app.services.user import get_user_info

router = APIRouter()

@router.get("/me", response_model=UserResponse, name="me", summary="Get current user info")
async def get_me(user_id: str = Depends(get_authenticated_user_id)):
    general_user = get_user_info(user_id)
    return general_user