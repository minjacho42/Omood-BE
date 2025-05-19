from fastapi import APIRouter, Response
from pydantic import BaseModel
from app.services.auth import login_with_code

router = APIRouter()

class CodePayload(BaseModel):
    code: str

@router.post("/login")
async def login(payload: CodePayload, response: Response):
    access_token = await login_with_code(payload.code)
    response.set_cookie(
        key="omood_at",
        value=access_token,
        httponly=True,
        max_age=3600,
        samesite="lax",
        secure=False,
    )
    return {"message": "Login success"}
