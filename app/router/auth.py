from urllib.parse import unquote
from quart import Blueprint, render_template, request, redirect, url_for
from quart_jwt_extended import set_access_cookies

from ..database import get_session
from .. import queries as qr

auth_router = Blueprint("auth_router", __name__)


@auth_router.route("/login", methods=["GET", "POST"])
async def login():
    next_url = request.args.get("next", url_for("index.index"))
    error_message = None

    if request.method == "POST":
        form = await request.form
        username = form.get("username")
        password = form.get("password")

        async with get_session() as session:
            token, err = await qr.login(session, username, password)

        if err:
            error_message = err

        else:
            external_token = token

            next_url = unquote(next_url)
            resp = redirect(next_url)

            set_access_cookies(resp, external_token)
            return resp

    return await render_template(
        "login.html", next=next_url, error_message=error_message
    )
