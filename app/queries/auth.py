from typing import Tuple, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Token
from ..queries import get_user_by_username


async def get_user_token(user_id: int):
    async with get_session() as session:
        result = await session.execute(select(Token).where(Token.user_id == user_id))
        return result.scalar_one_or_none()


async def login(
    session: AsyncSession, username: str, password: str
) -> Tuple[Optional[str], Optional[str]]:
    user, err = await get_user_by_username(username)

    if err:
        return None, err

    correct_password = await user.check_password(password)

    if not correct_password:
        return None, "password is incorrect"

    token = await get_user_token(user.id)

    if token is None:
        token = await user.generate_token()
        token = Token(user_id=user.id, token=token)

        session.add(token)
        await session.commit()

    else:
        token, err = await token.verify_token(user)

    return token.token, err
