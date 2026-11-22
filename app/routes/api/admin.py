from flask import Blueprint, request, jsonify, session
from app.security import login_required, admin_required
from app.models.user import list_users, get_user_by_id, update_user, update_token_balance
from app.models.story import list_all_stories
from app.services.analytics_service import summary, chart_data
from app.models.system_settings import list_settings
from app.db import query_db

bp = Blueprint("admin", __name__)


@bp.route("/users", methods=["GET"])
@login_required
@admin_required
def users():
    page = int(request.args.get("page", 1))
    role = request.args.get("role")
    search = request.args.get("search")
    is_active = request.args.get("is_active")
    ia = None if is_active is None else (is_active == "true" or is_active == "1")
    rows = list_users(search=search, role=role, is_active=ia, page=page)
    data = []
    for r in rows:
        d = dict(r)
        d.pop("password_hash", None)
        data.append(d)
    return jsonify({"success": True, "message": "OK", "data": {"users": data}})


@bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
@admin_required
def user_detail(user_id):
    u = get_user_by_id(user_id)
    if not u:
        return jsonify({"success": False, "message": "Not found", "error": {"code": "NOT_FOUND"}}), 404
    d = dict(u)
    d.pop("password_hash", None)
    return jsonify({"success": True, "message": "OK", "data": {"user": d}})


@bp.route("/users/<int:user_id>", methods=["PATCH"])
@login_required
@admin_required
def user_update(user_id):
    data = request.get_json(silent=True) or {}
    allowed = {"display_name", "phone_number", "role", "is_active", "username"}
    fields = {k: v for k, v in data.items() if k in allowed}
    update_user(user_id, fields, session["user_id"])
    return jsonify({"success": True, "message": "Updated", "data": {}})


@bp.route("/users/<int:user_id>/tokens", methods=["PATCH"])
@login_required
@admin_required
def user_tokens(user_id):
    data = request.get_json(silent=True) or {}
    if "token_balance" in data:
        update_token_balance(user_id, int(data["token_balance"]), session["user_id"])
    elif "adjustment" in data:
        from app.models.user import adjust_tokens
        adjust_tokens(user_id, int(data["adjustment"]), session["user_id"])
    return jsonify({"success": True, "message": "Updated", "data": {}})


@bp.route("/stories", methods=["GET"])
@login_required
@admin_required
def stories():
    page = int(request.args.get("page", 1))
    rows = list_all_stories(
        user_id=request.args.get("user_id", type=int),
        story_status=request.args.get("story_status"),
        generation_status=request.args.get("generation_status"),
        page=page,
    )
    return jsonify({"success": True, "message": "OK", "data": {"stories": [dict(r) for r in rows]}})


@bp.route("/analytics/summary", methods=["GET"])
@login_required
@admin_required
def analytics_summary():
    return jsonify({"success": True, "message": "OK", "data": summary()})


@bp.route("/analytics/charts", methods=["GET"])
@login_required
@admin_required
def analytics_charts():
    key = request.args.get("chart", "")
    return jsonify({"success": True, "message": "OK", "data": chart_data(key)})


@bp.route("/database/<table_name>", methods=["GET"])
@login_required
@admin_required
def db_viewer(table_name):
    allowed = {"tolstoy_users", "tolstoy_stories", "tolstoy_system_settings"}
    if table_name not in allowed:
        return jsonify({"success": False, "message": "Invalid table", "error": {"code": "VALIDATION_ERROR"}}), 400
    page = int(request.args.get("page", 1))
    per_page = 25
    offset = (page - 1) * per_page
    rows = query_db(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (per_page, offset))
    # strip secrets
    out = []
    for r in rows:
        d = dict(r)
        if "password_hash" in d:
            d["password_hash"] = "***"
        out.append(d)
    return jsonify({"success": True, "message": "OK", "data": {"rows": out, "table": table_name}})