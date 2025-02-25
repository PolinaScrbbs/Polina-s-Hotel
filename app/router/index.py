from quart import Blueprint, render_template, Response
from ..middleware import auth_check

index_router = Blueprint("index", __name__)


@index_router.route("/")
async def index():
    redirect, _ = await auth_check()
    if redirect:
        return redirect
    return await render_template("index.html", title="Main Page")
