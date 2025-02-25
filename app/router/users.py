from quart import Blueprint, render_template
from ..middleware import auth_check
from ..queries import get_users_list

users_router = Blueprint("users_router", __name__)


@users_router.route("/users")
async def table():
    current_user = await auth_check()
    users, err = await get_users_list()

    context = {
        "title": "Users Table",
        "current_user": current_user,
        "objects": users,
        "error_message": err.capitalize() if err else None,
        "add_url": "index.index",
    }

    return await render_template("users.html", **context)
