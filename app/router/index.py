from quart import Blueprint, render_template
from ..middleware import auth_check

index_router = Blueprint("index", __name__)


@index_router.route("/")
async def index():
    current_user = await auth_check()
    return await render_template("index.html", title="Main Page", user=current_user)
