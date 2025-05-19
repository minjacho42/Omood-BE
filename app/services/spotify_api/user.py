import requests
from fastapi import HTTPException
from app.models.spotify import SpotifyUser, RecentlyPlayedResponse

async def get_spotify_user_profile(access_token: str) -> SpotifyUser:
    """
    Spotify access_token을 이용하여 현재 로그인한 사용자의 프로필 정보를 반환합니다.

    Args:
        access_token (str): Spotify Web API에서 발급받은 access_token.

    Returns:
        SpotifyUser: 사용자의 ID, 이름, 이메일, 국가, 구독 유형, 프로필 이미지 등의 정보를 포함한 Pydantic 모델.

    Raises:
        HTTPException: Spotify API 호출 실패 시 예외 발생.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    resp = requests.get("https://api.spotify.com/v1/me", headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return SpotifyUser(**resp.json())


# 최근에 재생한 트랙 목록을 반환하는 함수
async def get_spotify_recently_played(access_token: str, limit: int = 20) -> RecentlyPlayedResponse:
    """
    Spotify access_token을 이용하여 최근에 재생한 트랙 목록을 반환합니다.

    Args:
        access_token (str): Spotify Web API에서 발급받은 access_token.
        limit (int): 반환할 트랙 수 (기본값: 20, 최대값: 50).

    Returns:
        RecentlyPlayedResponse: 각 재생 항목의 시각, 트랙, 앨범, 아티스트 정보 등을 포함한 Pydantic 모델.

    Raises:
        HTTPException: Spotify API 호출 실패 시 예외 발생.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "limit": limit
    }

    resp = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params=params)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return RecentlyPlayedResponse(**resp.json())
