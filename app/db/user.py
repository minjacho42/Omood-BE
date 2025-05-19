from app.db.session import SessionLocal
from app.models.spotify import SpotifyUser
from app.models.user import User, UserResponse
from typing import Optional

def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    with SessionLocal() as db:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            return UserResponse.model_validate(db_user)
        return None

def update_user(user: SpotifyUser) -> UserResponse:
    with SessionLocal() as db:
        db_user = db.query(User).filter(User.id == user.id).first()

        profile_image_url = user.images[0].url if user.images else None

        if db_user:
            # update existing user
            db_user.display_name = user.display_name
            db_user.email = user.email
            db_user.country = user.country
            db_user.product = user.product
            db_user.profile_image_url = profile_image_url
        else:
            # create new user
            db_user = User(
                id=user.id,
                display_name=user.display_name,
                email=user.email,
                country=user.country,
                product=user.product,
                profile_image_url=profile_image_url,
            )
            db.add(db_user)
        db.commit()
        return UserResponse.model_validate(db_user)
