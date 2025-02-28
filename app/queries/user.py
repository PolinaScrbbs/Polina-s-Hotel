from datetime import datetime
from typing import Tuple, Optional, List

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import User, Role, Gender


async def get_user_by_username(username: str) -> Tuple[Optional[User], Optional[str]]:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if user is None:
            return None, "user not found"

        return user, None


async def get_user_by_id(
    user_id: int,
) -> Tuple[Optional[AsyncSession], Optional[User], Optional[str]]:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))

        user = result.scalar_one_or_none()

        if user is None:
            return None, None, "user not found"

        return session, user, None


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


async def update_user(
    session: AsyncSession, user: User, data: dict
) -> Tuple[bool, Optional[str]]:
    user.username = data.get("username", user.username)
    user.name = data.get("name", user.name)
    user.surname = data.get("surname", user.surname)
    user.patronymic = data.get("patronymic", user.patronymic)

    date_of_birth = data.get("date_of_birth", user.date_of_birth)
    if isinstance(date_of_birth, str):
        try:
            user.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"

    user.phone_number = data.get("phone_number", user.phone_number)
    user.registration_address = data.get(
        "registration_address", user.registration_address
    )
    user.gender = Gender(data.get("gender", user.gender))
    user.role = Role(data.get("role", user.role))

    await session.merge(user)
    await session.commit()
    return True, None


async def delete_user(user_id: int) -> Tuple[bool, Optional[str]]:
    session, user, err = await get_user_by_id(user_id)

    if err:
        return False, err

    await session.delete(user)
    await session.commit()
    return True, None
