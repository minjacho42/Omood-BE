from app.models.user import User
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils.logging import logger

logger = logger.bind(layer="repository", module="user")

async def get_user_by_id(user_id: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    return user

async def update_user(user: User, db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(
            (User.provider == user.provider) &
            (User.provider_id == user.provider_id)
        )
    )
    db_user = result.scalars().first()

    if db_user:
        db_user.name = user.name
        db_user.email = user.email
        db_user.picture = user.picture
        user = db_user
    else:
        user.id = str(uuid.uuid4())
        db.add(user)

    await db.commit()
    return user
