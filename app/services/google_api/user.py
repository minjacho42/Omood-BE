import requests
from fastapi import HTTPException
from loguru import logger
from app.models.user import User

def get_user_with_token(access_token: str) -> User:
    """
    Google access_token으로 사용자 정보를 요청합니다.

    Args:
        access_token (str): Google에서 발급받은 access token.

    Returns:
        User: 사용자 정보 (id, email, name, picture 등)

    Raises:
        HTTPException: 요청 실패 시 400 상태 코드로 예외 발생.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    resp = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
    if resp.status_code != 200:
        logger.bind(event="google_userinfo").error(resp.text)
        raise HTTPException(status_code=400)
    user = User()
    user.provider = "google"
    user.provider_id = resp.json()["id"]
    user.email = resp.json()["email"]
    user.name = resp.json()["name"]
    user.picture = resp.json()["picture"]
    logger.bind(event="google_userinfo").info(user)
    return user