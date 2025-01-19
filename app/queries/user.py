from typing import Tuple, Optional

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User


async def get_user_by_username(
    session: AsyncSession, username: str
) -> Tuple[Optional[User], Optional[str]]:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        return None, "user not found"

    return user, None


async def get_user_by_id(
    session: AsyncSession, user_id: int
) -> Tuple[Optional[User], Optional[str]]:
    result = await session.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()

    if user is None:
        return None, "user not found"

    return user, None
