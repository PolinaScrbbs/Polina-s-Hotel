from quart import Blueprint, render_template, jsonify, request, redirect, url_for
from ..middleware import auth_check, role_check
from ..models import Role
from ..queries import (
    get_users_list,
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
)
from ..validators import UserValidator, UserUpdateValidator

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

    return await render_template("add_user.html", **context)


@users_router.route("/user/details")
async def details():
    user_id = int(request.args.get("id"))
    auth_redirect, current_user = await auth_check()
    if auth_redirect:
        return auth_redirect

    message = await role_check(
        current_user.role, [Role.ADMIN], "only the admin has access"
    )
    if message:
        return jsonify({"message": message})

    _, user, _ = await get_user_by_id(user_id)

    context = {
        "title": "User Details",
        "detail_text": f"@{user.username}",
        "update_url": "users_router.update",
        "delete_url": "users_router.delete",
        "object": user,
    }
    return await render_template("user_details.html", **context)


@users_router.route("/user/update", methods=["GET", "POST"])
async def update():
    user_id = int(request.args.get("id"))

    auth_redirect, current_user = await auth_check()
    if auth_redirect:
        return auth_redirect

    message = await role_check(
        current_user.role, [Role.ADMIN], "only the admin has access"
    )
    if message:
        return jsonify({"message": message})

    session, user, _ = await get_user_by_id(user_id)

    context = {"title": "Update User", "user": user, "error_message": ""}

    if request.method == "POST":
        data = await request.form
        validator = UserUpdateValidator(data)

        error_message = await validator.validate(user)
        if error_message:
            context["error_message"] = error_message
            return await render_template("user_update.html", **context)

        _, error_message = await update_user(session, user, data)
        if error_message:
            context["error_message"] = error_message
            return await render_template("user_update.html", **context)

        return redirect(url_for("users_router.details", id=user_id))

    return await render_template("user_update.html", **context)


@users_router.route("/user/delete")
async def delete():
    user_id = int(request.args.get("id"))

    auth_redirect, current_user = await auth_check()
    if auth_redirect:
        return auth_redirect

    message = await role_check(
        current_user.role, [Role.ADMIN], "only the admin has access"
    )
    if message:
        return jsonify({"message": message})

    _, err = await delete_user(user_id)

    if err:
        return jsonify({"error": err})

    return redirect(url_for("users_router.table"))
