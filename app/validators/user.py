import re
from datetime import datetime
from typing import Tuple, Optional, Dict
from sqlalchemy import select, exists

from ..database import get_session
from ..models import User, Role, Gender


class UserValidator:
    def __init__(self, form_data):
        self.form_data = form_data

    async def validate(self) -> Tuple[Optional[User], Optional[str]]:
        username_error = await self.username_validate()
        if username_error:
            return None, username_error

        password_error = await self.password_validate()
        if password_error:
            return None, password_error

        name_error = await self.name_validate()
        if name_error:
            return None, name_error

        surname_error = await self.surname_validate()
        if surname_error:
            return None, surname_error

        patronymic_error = await self.patronymic_validate()
        if patronymic_error:
            return None, patronymic_error

        date_of_birth_error = await self.date_of_birth_validate()
        if date_of_birth_error:
            return None, date_of_birth_error

        phone_number_error = await self.phone_number_validate()
        if phone_number_error:
            return None, phone_number_error

        registration_address_error = await self.registration_address_validate()
        if registration_address_error:
            return None, registration_address_error

        gender_error = await self.gender_validate()
        if gender_error:
            return None, gender_error

        role_error = await self.role_validate()
        if role_error:
            return None, role_error

        return await self.create_user(), None

    async def create_user(self) -> User:
        user_data = {
            "name": self.form_data["name"],
            "surname": self.form_data["surname"],
            "patronymic": self.form_data.get("patronymic", ""),
            "username": self.form_data["username"],
            "date_of_birth": datetime.strptime(
                self.form_data["date_of_birth"], "%Y-%m-%d"
            ).date(),
            "phone_number": self.form_data["phone_number"],
            "registration_address": self.form_data["registration_address"],
            "gender": Gender(self.form_data["gender"]),
            "role": Role(self.form_data["role"]),
        }

        user = User(**user_data)
        await user.set_password(self.form_data["password"])

        return user

    async def username_validate(self) -> Optional[str]:
        username = self.form_data.get("username")
        if not username:
            return "Username is required"
        if await exists_user_by_username(username):
            return "User with this username is already there"
        if len(username) < 4 or len(username) > 20:
            return "Username must be between 4 and 20 characters"
        if not re.match(r"^[A-Za-z0-9]+$", username):
            return "Username must contain only letters and digits"
        return None

    async def password_validate(self) -> Optional[str]:
        password = self.form_data.get("password")
        if not password:
            return "Password is required"
        if len(password) < 8 or len(password) > 20:
            return "Password must be between 8 and 20 characters"
        if not re.search(r"[A-Za-z]", password) or not re.search(
            r"[0-9]", self.form_data["password"]
        ):
            return "Password must contain both letters and numbers"
        if password != self.form_data.get("confirm_password"):
            return "Passwords do not match"
        return None

    async def name_validate(self) -> Optional[str]:
        name = self.form_data.get("name")
        if not name:
            return "Name is required"
        if not re.match(r"^[А-Яа-я]+$", name):
            return "Name must contain only Russian letters"
        if len(name) < 2 or len(name) > 50:
            return "Name must be between 2 and 50 characters"
        return None

    async def surname_validate(self) -> Optional[str]:
        surname = self.form_data.get("surname")
        if not surname:
            return "Surname is required"
        if not re.match(r"^[А-Яа-я]+$", surname):
            return "Surname must contain only Russian letters"
        if len(surname) < 2 or len(surname) > 50:
            return "Surname must be between 2 and 50 characters"
        return None

    async def patronymic_validate(self) -> Optional[str]:
        patronymic = self.form_data.get("patronymic")
        if patronymic and not re.match(r"^[А-Яа-я]+$", patronymic):
            return "Patronymic must contain only Russian letters"
        if patronymic and (len(patronymic) < 2 or len(patronymic) > 50):
            return "Patronymic must be between 2 and 50 characters"
        return None

    async def date_of_birth_validate(self) -> Optional[str]:
        if not self.form_data.get("date_of_birth"):
            return "Date of birth is required"
        return None

    async def phone_number_validate(self) -> Optional[str]:
        phone_number = self.form_data.get("phone_number")
        if not phone_number:
            return "Phone number is required"
        if not re.match(r"^\+?[0-9]{10,15}$", phone_number):
            return "Invalid phone number format"
        return None

    async def registration_address_validate(self) -> Optional[str]:
        registration_address = self.form_data.get("registration_address")
        if not registration_address:
            return "Registration address is required"
        if len(registration_address) < 5 or len(registration_address) > 100:
            return "Registration address must be between 5 and 100 characters"
        if not re.match(r"^[A-Za-zА-Яа-я0-9 ,.-:]+$", registration_address):
            return "Registration address can only contain letters, numbers, and the following symbols: , . - :"
        return None

    async def gender_validate(self) -> Optional[str]:
        if Gender(self.form_data.get("gender")) not in Gender:
            return "Invalid gender"
        return None

    async def role_validate(self) -> Optional[str]:
        if Role(self.form_data.get("role")) not in Role:
            return "Invalid role"
        return None


class UserUpdateValidator:
    def __init__(self, form_data: Dict[str, str]):
        self.form_data = form_data

    async def validate(self, user: User) -> Optional[str]:
        if "username" in self.form_data:
            username_error = await self.username_validate(user)
            if username_error:
                return username_error

        if "password" in self.form_data:
            password_error = await self.password_validate()
            if password_error:
                return password_error

        if "name" in self.form_data:
            name_error = await self.name_validate()
            if name_error:
                return name_error

        if "surname" in self.form_data:
            surname_error = await self.surname_validate()
            if surname_error:
                return surname_error

        if "patronymic" in self.form_data:
            patronymic_error = await self.patronymic_validate()
            if patronymic_error:
                return patronymic_error

        if "date_of_birth" in self.form_data:
            date_of_birth_error = await self.date_of_birth_validate()
            if date_of_birth_error:
                return date_of_birth_error

        if "phone_number" in self.form_data:
            phone_number_error = await self.phone_number_validate()
            if phone_number_error:
                return phone_number_error

        if "registration_address" in self.form_data:
            registration_address_error = await self.registration_address_validate()
            if registration_address_error:
                return registration_address_error

        if "gender" in self.form_data:
            gender_error = await self.gender_validate()
            if gender_error:
                return gender_error

        if "role" in self.form_data:
            role_error = await self.role_validate()
            if role_error:
                return role_error

        return None

    async def username_validate(self, user: User) -> Optional[str]:
        username = self.form_data.get("username")
        if username == user.username:
            return None
        if await exists_user_by_username(username):
            return "User with this username already exists"
        if len(username) < 4 or len(username) > 20:
            return "Username must be between 4 and 20 characters"
        if not re.match(r"^[A-Za-z0-9]+$", username):
            return "Username must contain only letters and digits"
        return None

    async def password_validate(self) -> Optional[str]:
        password = self.form_data.get("password")
        if len(password) < 8 or len(password) > 20:
            return "Password must be between 8 and 20 characters"
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            return "Password must contain both letters and numbers"
        return None

    async def name_validate(self) -> Optional[str]:
        name = self.form_data.get("name")
        if not re.match(r"^[А-Яа-я]+$", name):
            return "Name must contain only Russian letters"
        if len(name) < 2 or len(name) > 50:
            return "Name must be between 2 and 50 characters"
        return None

    async def surname_validate(self) -> Optional[str]:
        surname = self.form_data.get("surname")
        if not re.match(r"^[А-Яа-я]+$", surname):
            return "Surname must contain only Russian letters"
        if len(surname) < 2 or len(surname) > 50:
            return "Surname must be between 2 and 50 characters"
        return None

    async def patronymic_validate(self) -> Optional[str]:
        patronymic = self.form_data.get("patronymic")
        if patronymic and not re.match(r"^[А-Яа-я]+$", patronymic):
            return "Patronymic must contain only Russian letters"
        if patronymic and (len(patronymic) < 2 or len(patronymic) > 50):
            return "Patronymic must be between 2 and 50 characters"
        return None

    async def date_of_birth_validate(self) -> Optional[str]:
        try:
            datetime.strptime(self.form_data["date_of_birth"], "%Y-%m-%d")
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD"
        return None

    async def phone_number_validate(self) -> Optional[str]:
        phone_number = self.form_data.get("phone_number")
        if not re.match(r"^\+?[0-9]{10,15}$", phone_number):
            return "Invalid phone number format"
        return None

    async def registration_address_validate(self) -> Optional[str]:
        registration_address = self.form_data.get("registration_address")
        if len(registration_address) < 5 or len(registration_address) > 100:
            return "Registration address must be between 5 and 100 characters"
        if not re.match(r"^[A-Za-zА-Яа-я0-9 ,.-:]+$", registration_address):
            return "Registration address can only contain letters, numbers, and the following symbols: , . - :"
        return None

    async def gender_validate(self) -> Optional[str]:
        try:
            Gender(self.form_data.get("gender"))
        except ValueError:
            return "Invalid gender"
        return None

    async def role_validate(self) -> Optional[str]:
        try:
            Role(self.form_data.get("role"))
        except ValueError:
            return "Invalid role"
        return None


async def exists_user_by_username(username: str) -> bool:
    async with get_session() as session:
        query = select(exists().where(User.username == username))
        result = await session.execute(query)
        return result.scalar()
