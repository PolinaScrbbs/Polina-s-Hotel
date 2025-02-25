from typing import Tuple, Optional
from quart import Response, request, redirect, url_for
from ..models import User
from ..queries import get_current_user


async def auth_check() -> Tuple[Optional[Response], Optional[User]]:
    token = request.cookies.get("access_token")

    if not token:
        next_url = request.url
        return redirect(url_for("auth_router.login", next=next_url)), None

    current_user = await get_current_user(token)
    if current_user is None:
        next_url = request.url
        return redirect(url_for("auth_router.login", next=next_url)), None

    return None, current_user
