from flask import Blueprint, request, jsonify, session
from app.db import get_db
from app.models.user import (create_user, get_user_by_username, get_user_by_id,
                            verify_password, now_iso)
from app.security import login_required
from app.schemas.validators import require_fields, validate_username, validate_password
from app.models.system_settings import get_setting_value

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["username", "password"])
    if err:
        return jsonify({"success": False, "message": err, "error": {"code": "VALIDATION_ERROR"}}), 400
    if not validate_username(data["username"]):
        return jsonify({"success": False, "message": "Invalid username", "error": {"code": "VALIDATION_ERROR"}}), 400
    if not validate_password(data["password"]):
        return jsonify({"success": False, "message": "Password too weak", "error": {"code": "VALIDATION_ERROR"}}), 400
    if get_user_by_username(data["username"]):
        return jsonify({"success": False, "message": "Username taken", "error": {"code": "CONFLICT"}}), 409
    uid = create_user(data["username"], data["password"], data.get("display_name"), data.get("phone_number"), role="USER", created_by=None)
    return jsonify({"success": True, "message": "Registered", "data": {"user_id": uid}}), 201


@bp.route("/user/login", methods=["POST"])
def user_login():
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["username", "password"])
    if err:
        return jsonify({"success": False, "message": err, "error": {"code": "VALIDATION_ERROR"}}), 400
    u = get_user_by_username(data["username"])
    if not u or not verify_password(u, data["password"]):
        return jsonify({"success": False, "message": "Invalid credentials", "error": {"code": "UNAUTHORIZED"}}), 401
    if not u["is_active"]:
        return jsonify({"success": False, "message": "Account inactive", "error": {"code": "FORBIDDEN"}}), 403
    session["user_id"] = u["id"]
    session["role"] = u["role"]
    session["username"] = u["username"]
    return jsonify({"success": True, "message": "Logged in", "data": {"user_id": u["id"], "role": u["role"]}})


@bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["username", "password"])
    if err:
        return jsonify({"success": False, "message": err, "error": {"code": "VALIDATION_ERROR"}}), 400
    u = get_user_by_username(data["username"])
    if not u or not verify_password(u, data["password"]):
        return jsonify({"success": False, "message": "Invalid credentials", "error": {"code": "UNAUTHORIZED"}}), 401
    if u["role"] not in ("ADMIN", "SUPER_ADMIN"):
        return jsonify({"success": False, "message": "Not an admin", "error": {"code": "FORBIDDEN"}}), 403
    if not u["is_active"]:
        return jsonify({"success": False, "message": "Account inactive", "error": {"code": "FORBIDDEN"}}), 403
    session["user_id"] = u["id"]
    session["role"] = u["role"]
    session["username"] = u["username"]
    return jsonify({"success": True, "message": "Logged in", "data": {"user_id": u["id"], "role": u["role"]}})


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out", "data": {}})


@bp.route("/me", methods=["GET"])
@login_required
def me():
    from app.models.user import get_user_by_id
    u = get_user_by_id(session["user_id"])
    if not u:
        session.clear()
        return jsonify({"success": False, "message": "Unauthorized", "error": {"code": "UNAUTHORIZED"}}), 401
    return jsonify({"success": True, "message": "OK", "data": {
        "user_id": u["id"], "username": u["username"], "display_name": u["display_name"],
        "role": u["role"], "token_balance": u["token_balance"], "is_active": bool(u["is_active"]),
    }})


@bp.route("/csrf", methods=["GET"])
def csrf_token():
    from flask_wtf.csrf import generate_csrf
    return jsonify({"success": True, "message": "OK", "data": {"csrf_token": generate_csrf()}})