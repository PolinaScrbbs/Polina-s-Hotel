from typing import Union
from quart import Response, request, redirect, url_for
from ..models import User
from ..queries import get_current_user


async def auth_check() -> Union[Response, User]:
    token = request.cookies.get("access_token")

    if not token:
        next_url = request.url
        return redirect(url_for("auth_router.login", next=next_url))

    current_user = await get_current_user(token)
    return current_user
