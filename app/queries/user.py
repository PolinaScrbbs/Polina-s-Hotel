from typing import Tuple, Optional, List

from sqlalchemy.future import select

from ..database import get_session
from ..models import User, Role


async def get_user_by_username(username: str) -> Tuple[Optional[User], Optional[str]]:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if user is None:
            return None, "user not found"

        return user, None


async def get_user_by_id(user_id: int) -> Tuple[Optional[User], Optional[str]]:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))

        user = result.scalar_one_or_none()

        if user is None:
            return None, "user not found"

        return user, None


async def get_users_list() -> Tuple[Optional[List[User]], Optional[str]]:
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.role == Role.USER).order_by(User.username)
        )

        users = result.scalars().all()

        if not users:
            return None, "users list is empty"

        return users, None


async def create_user(new_user: User) -> Tuple[bool, Optional[str]]:
    async with get_session() as session:
        session.add(new_user)
        await session.commit()
        return True, None
