import uuid

import bcrypt
import jwt
from typing import Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum as BaseEnum

import pytz
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Enum,
    Date,
    CHAR,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Base, get_session
from ..config import config as conf


class Gender(BaseEnum):
    MALE = "male"
    FEMALE = "female"


class Role(BaseEnum):
    USER = "user"
    CLIENT = "client"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    surname = Column(String(64), nullable=False)
    patronymic = Column(String(64), nullable=False)
    username = Column(String(20), unique=True, nullable=False)
    hashed_password = Column(String(512), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    phone_number = Column(CHAR(12), unique=True, nullable=False)
    registration_address = Column(String(128), nullable=False)
    gender = Column(Enum(Gender), default=Gender.MALE, nullable=False)
    role = Column(Enum(Role), default=Role.USER, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    async def set_password(self, password: str) -> None:
        self.hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    async def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        )

    async def generate_token(self, token_lifetime: int = conf.token_lifetime) -> str:
        payload = {
            "identity": self.id,
            "exp": datetime.now(pytz.timezone("Europe/Moscow"))
            + timedelta(seconds=token_lifetime),
            "csrf": str(uuid.uuid4()),
        }
        return jwt.encode(payload, conf.secret, algorithm="HS256")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    async def verify_token(
        self, user: Optional[User]
    ) -> Tuple[Optional[object], Optional[str]]:
        async with get_session() as session:
            try:
                jwt.decode(self.token, conf.secret, algorithms=["HS256"])
                return self, None

            except jwt.ExpiredSignatureError:
                return await self.refresh_token(session, user)

            except jwt.InvalidTokenError:
                return None, "token is invalid"

    async def refresh_token(
        self, session: AsyncSession, user: Optional[User]
    ) -> Tuple[Optional[object], Optional[str]]:
        if user is None:
            return None, "token has expired"

        new_token = await user.generate_token()

        self.token = new_token
        session.add(self)
        await session.commit()

        return self, None
