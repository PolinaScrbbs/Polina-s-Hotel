import asyncio
import argparse
import datetime
from quart import Quart
from quart_jwt_extended import JWTManager

from .config import config as conf
from .database import get_session
from .models import User, Gender, Role
from .router import index_router, auth_router, users_router

app = Quart(__name__, static_folder="static", template_folder="templates")

app.config["JWT_SECRET_KEY"] = conf.secret
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_CSRF_PROTECT"] = True

jwt = JWTManager(app)

app.register_blueprint(index_router)
app.register_blueprint(auth_router)
app.register_blueprint(users_router)


async def create_superuser():
    async with get_session() as session:
        admin = User(
            name="Тимофей",
            surname="Ивановский",
            patronymic="Владиславович",
            username="PolinaScrbbs",
            date_of_birth=datetime.date.today(),
            phone_number="+79513171214",
            registration_address="Дом Пушкина, дом Колотушкина",
            gender=Gender.MALE,
            role=Role.ADMIN,
        )

        await admin.set_password("Que337")
        session.add(admin)
        await session.commit()
        print("Суперпользователь создан!")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Запуск приложения с параметрами")
    parser.add_argument(
        "--create-superuser",
        action="store_true",
        default=False,
        help="Создать суперпользователя перед запуском приложения",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.create_superuser:
        asyncio.run(create_superuser())

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
