from quart import Blueprint, render_template, jsonify, request, redirect, url_for
from ..middleware import auth_check, role_check
from ..models import User, Role, Gender
from ..queries import get_users_list, create_user
from ..validators import UserValidator

users_router = Blueprint("users_router", __name__)


@users_router.route("/users")
async def table():
    auth_redirect, current_user = await auth_check()
    if auth_redirect:
        return auth_redirect

    message = await role_check(
        current_user.role, [Role.ADMIN], "only the admin has access"
    )
    if message:
        return jsonify({"message": message})

    users, err = await get_users_list()

    context = {
        "title": "Users Table",
        "current_user": current_user,
        "objects": users,
        "error_message": err.capitalize() if err else None,
        "add_url": "users_router.add",
    }

    return await render_template("users.html", **context)


@users_router.route("/add_users", methods=["GET", "POST"])
async def add():
    auth_redirect, current_user = await auth_check()
    if auth_redirect:
        return auth_redirect

    message = await role_check(
        current_user.role, [Role.ADMIN], "only the admin has access"
    )
    if message:
        return jsonify({"message": message})

    context = {"title": "Add New People", "form_data": {}}

    if request.method == "POST":
        form_data = await request.form
        validator = UserValidator(form_data)

        new_user, error = await validator.validate()
        if not error:
            result, _ = await create_user(new_user)
            if result:
                return redirect(url_for("users_router.table"))

        context["error_message"] = error
        context["form_data"] = form_data

    print(context)
    return await render_template("add_user.html", **context)
