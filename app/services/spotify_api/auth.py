import requests
from app.core.config import settings
from fastapi import HTTPException
from loguru import logger

def get_token_with_code(code: str) -> dict:
    """
    Spotify의 OAuth 인증 코드로 access_token과 refresh_token을 요청합니다.

    Args:
        code (str): Spotify 인증 절차에서 발급받은 authorization code.

    Returns:
        dict: 다음 키들을 포함하는 JSON 형태의 토큰 정보입니다.
            - access_token (str): Spotify Web API 요청에 사용될 액세스 토큰.
            - token_type (str): 토큰 타입 (일반적으로 "Bearer").
            - scope (str): access_token으로 접근 가능한 권한(scope) 목록 (공백으로 구분된 문자열).
            - expires_in (int): access_token의 유효 시간 (초 단위).
            - refresh_token (str): access_token 재발급에 사용할 수 있는 토큰.

    Raises:
        HTTPException: 인증 실패 시 400 상태 코드와 함께 예외 발생.
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post("https://accounts.spotify.com/api/token", data=data, headers=headers)
    if resp.status_code != 200:
        logger.bind(event="spotify_auth").error(resp.text)
        raise HTTPException(status_code=400)
    token_dict = resp.json()

    return token_dict

async def get_spotify_token_rt(refresh_token: str) -> dict:
    """
    Spotify의 refresh_token을 이용하여 새로운 access_token을 발급받습니다.

    Args:
        refresh_token (str): 이전에 발급받은 Spotify refresh_token.

    Returns:
        dict: 다음 키들을 포함하는 JSON 형태의 토큰 정보입니다.
            - access_token (str): 새롭게 발급된 Spotify Web API access_token.
            - token_type (str): 토큰 타입 (일반적으로 "Bearer").
            - scope (str): access_token으로 접근 가능한 권한 목록.
            - expires_in (int): access_token의 유효 시간 (초 단위).
            - refresh_token (str, optional): 경우에 따라 새롭게 발급된 refresh_token.

    Raises:
        HTTPException: 토큰 갱신 실패 시 400 상태 코드와 함께 예외 발생.
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post("https://accounts.spotify.com/api/token", data=data, headers=headers)
    if resp.status_code != 200:
        logger.bind(event="spotify_refresh").error(resp.text)
        raise HTTPException(status_code=400)
    refreshed_token = resp.json()

    return refreshed_token
