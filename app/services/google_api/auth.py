import requests
from app.core.config import settings
from fastapi import HTTPException
from loguru import logger


def get_token_with_code(code: str) -> dict:
    """
    Google OAuth 인증 코드로 access_token과 id_token을 요청합니다.

    Args:
        code (str): Google OAuth 인증 과정에서 발급받은 authorization code.

    Returns:
        dict: 다음 키들을 포함하는 JSON 형태의 토큰 정보입니다.
            - access_token (str): Google API 요청에 사용될 액세스 토큰.
            - expires_in (int): access_token의 유효 시간 (초 단위).
            - id_token (str): 사용자 정보를 포함한 JWT 토큰.
            - scope (str): access_token으로 접근 가능한 권한(scope) 목록 (공백으로 구분된 문자열).
            - token_type (str): 토큰 타입 (일반적으로 "Bearer").
            - refresh_token (str): access_token 재발급에 사용할 수 있는 토큰 (옵션).

    Raises:
        HTTPException: 인증 실패 시 400 상태 코드와 함께 예외 발생.
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.REDIRECT_URI,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post("https://oauth2.googleapis.com/token", data=data, headers=headers)
    if resp.status_code != 200:
        logger.bind(event="google_auth").error(resp.text)
        raise HTTPException(status_code=400)
    token_dict = resp.json()

    return token_dict