from app.models.spotify import SpotifyUser
from app.db.user import update_user, get_user_by_id
from app.utils.redis import redis_client

async def create_or_update_user(user_info: SpotifyUser, tokens: dict):
    user = update_user(user_info)
    await redis_client.setex(f"spotify:at:{user.id}", int(tokens.get("expires_in")), tokens.get("access_token"))
    await redis_client.set(f"spotify:rt:{user.id}", tokens.get("refresh_token"))
    await redis_client.rpush("spotify:subscribers", user.id)
    return user

def get_user_info(user_id: str):
    return get_user_by_id(user_id)