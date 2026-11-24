import re
import sqlite3
from flask import Blueprint, request, jsonify, session
from app.security import (login_required, admin_required, permission_required,
                          VALID_ROLES, ADMIN_CAPABILITIES, SUPER_ONLY_CAPABILITIES,
                          permissions_for)
from app.models.user import (list_users, get_user_by_id, update_user, adjust_tokens,
                             count_users, count_active_users)
from app.models.story import list_all_stories
from app.services.analytics_service import summary, chart_data, db_health, integrity_check, recent_activity
from app.models.system_settings import list_settings, set_setting, get_setting_value
from app.db import query_db
from app.schemas.validators import validate_username

bp = Blueprint("admin", __name__)

DB_TABLES = {"tolstoy_users", "tolstoy_stories", "tolstoy_system_settings"}
SEARCH_COLUMNS = {
    "tolstoy_users": ("username", "display_name", "phone_number", "role"),
    "tolstoy_stories": ("title", "content", "language", "generation_status", "story_status"),
    "tolstoy_system_settings": ("setting_key", "description"),
}


def _fail(code, message, status=400):
    return jsonify({"success": False, "message": message, "error": {"code": code}}), status


def _actor():
    return get_user_by_id(session["user_id"])


def _password_ok(password):
    actor = _actor()
    from app.models.user import verify_password
    return bool(actor and isinstance(password, str) and verify_password(actor, password))


def _active_super_admins():
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_users WHERE role='SUPER_ADMIN' AND is_active=1", one=True)
    return r["c"] if r else 0


@bp.route("/users", methods=["GET"])
@login_required
@admin_required
@permission_required("users_view")
def users():
    page = max(1, request.args.get("page", 1, type=int))
    role = request.args.get("role")
    search = request.args.get("search")
    is_active = request.args.get("is_active")
    ia = None if is_active is None else (is_active in ("true", "1"))
    rows = list_users(search=search, role=role, is_active=ia, page=page)
    where, args = ["1=1"], []
    if search:
        where.append("(username LIKE ? OR display_name LIKE ?)")
        args += [f"%{search}%", f"%{search}%"]
    if role:
        where.append("role=?")
        args.append(role)
    if ia is not None:
        where.append("is_active=?")
        args.append(1 if ia else 0)
    total = query_db(f"SELECT COUNT(*) AS c FROM tolstoy_users WHERE {' AND '.join(where)}", tuple(args), one=True)["c"]
    data = []
    for r in rows:
        d = dict(r)
        d.pop("password_hash", None)
        data.append(d)
    return jsonify({"success": True, "message": "OK", "data": {"users": data, "total": total, "page": page}})


@bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
@admin_required
@permission_required("users_view")
def user_detail(user_id):
    u = get_user_by_id(user_id)
    if not u:
        return _fail("NOT_FOUND", "Not found", 404)
    d = dict(u)
    d.pop("password_hash", None)
    return jsonify({"success": True, "message": "OK", "data": {"user": d}})


@bp.route("/users/<int:user_id>", methods=["PATCH"])
@login_required
@admin_required
@permission_required("users_edit")
def user_update(user_id):
    target = get_user_by_id(user_id)
    if not target:
        return _fail("NOT_FOUND", "Not found", 404)
    data = request.get_json(silent=True) or {}
    fields = {}
    if "username" in data:
        name = str(data["username"]).strip()
        if not validate_username(name):
            return _fail("VALIDATION_ERROR", "Invalid username")
        other = query_db("SELECT id FROM tolstoy_users WHERE username=?", (name,), one=True)
        if other and other["id"] != user_id:
            return _fail("CONFLICT", "Username already taken", 409)
        fields["username"] = name
    if "display_name" in data:
        name = str(data["display_name"] or "").strip()
        if len(name) > 80:
            return _fail("VALIDATION_ERROR", "Display name too long")
        fields["display_name"] = name or None
    if "phone_number" in data:
        phone = str(data["phone_number"] or "").strip()
        if phone and not re.match(r"^\+?[0-9][0-9\s-]{4,19}$", phone):
            return _fail("VALIDATION_ERROR", "Invalid phone number")
        if phone:
            other = query_db("SELECT id FROM tolstoy_users WHERE phone_number=?", (phone,), one=True)
            if other and other["id"] != user_id:
                return _fail("CONFLICT", "Phone number already taken", 409)
        fields["phone_number"] = phone or None
    if "is_active" in data:
        active = data["is_active"] in (True, 1, "true", "1")
        if not active:
            if user_id == session["user_id"]:
                return _fail("FORBIDDEN", "You cannot deactivate yourself", 403)
            if target["role"] == "SUPER_ADMIN" and _active_super_admins() <= 1:
                return _fail("FORBIDDEN", "At least one active SUPER_ADMIN is required", 403)
        fields["is_active"] = 1 if active else 0
    if not fields:
        return _fail("VALIDATION_ERROR", "No editable fields provided")
    try:
        update_user(user_id, fields, session["user_id"])
    except sqlite3.IntegrityError:
        return _fail("CONFLICT", "Username or phone already taken", 409)
    return jsonify({"success": True, "message": "Updated", "data": {}})


@bp.route("/users/<int:user_id>/tokens", methods=["PATCH"])
@login_required
@admin_required
@permission_required("wallet_edit")
def user_tokens(user_id):
    data = request.get_json(silent=True) or {}
    if "token_balance" in data or "adjustment" in data:
        return _fail("TOKEN_DECREASE_FORBIDDEN", "Token balances can only be increased")
    amount = data.get("increase")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0 or amount > 100000:
        return _fail("VALIDATION_ERROR", "Increase must be a positive integer")
    if not get_user_by_id(user_id):
        return _fail("NOT_FOUND", "Not found", 404)
    adjust_tokens(user_id, amount, session["user_id"])
    new = get_user_by_id(user_id)["token_balance"]
    return jsonify({"success": True, "message": "Tokens added", "data": {"token_balance": new}})


@bp.route("/users/<int:user_id>/role", methods=["PATCH"])
@login_required
@admin_required
@permission_required("roles_manage")
def user_role(user_id):
    data = request.get_json(silent=True) or {}
    target = get_user_by_id(user_id)
    if not target:
        return _fail("NOT_FOUND", "Not found", 404)
    role = data.get("role")
    if role not in VALID_ROLES:
        return _fail("VALIDATION_ERROR", "Invalid role")
    if not _password_ok(data.get("password")):
        return _fail("UNAUTHORIZED", "Invalid password", 401)
    if user_id == session["user_id"]:
        return _fail("FORBIDDEN", "You cannot change your own role", 403)
    if target["role"] == "SUPER_ADMIN" and role != "SUPER_ADMIN" and target["is_active"] and _active_super_admins() <= 1:
        return _fail("FORBIDDEN", "At least one active SUPER_ADMIN is required", 403)
    update_user(user_id, {"role": role}, session["user_id"])
    return jsonify({"success": True, "message": "Role updated", "data": {"role": role}})


@bp.route("/roles/permissions", methods=["GET"])
@login_required
@admin_required
@permission_required("roles_view")
def get_permissions():
    stored = get_setting_value("role_permissions", {}) or {}
    return jsonify({"success": True, "message": "OK", "data": {
        "permissions": stored,
        "capabilities": ADMIN_CAPABILITIES,
        "locked": sorted(SUPER_ONLY_CAPABILITIES),
        "editable": "roles_manage" in permissions_for(),
    }})


@bp.route("/roles/permissions", methods=["PUT"])
@login_required
@admin_required
@permission_required("roles_manage")
def put_permissions():
    data = request.get_json(silent=True) or {}
    matrix = data.get("permissions")
    if not isinstance(matrix, dict):
        return _fail("VALIDATION_ERROR", "Invalid permission matrix")
    clean = {}
    for role in VALID_ROLES:
        if role == "SUPER_ADMIN":
            clean[role] = ["*"]
            continue
        values = matrix.get(role, [])
        if not isinstance(values, list) or any(v not in ADMIN_CAPABILITIES for v in values):
            return _fail("VALIDATION_ERROR", f"Invalid capabilities for {role}")
        if set(values) & SUPER_ONLY_CAPABILITIES:
            return _fail("FORBIDDEN", "Some capabilities are SUPER_ADMIN only", 403)
        clean[role] = values
    actor_role = session.get("role")
    if actor_role != "SUPER_ADMIN" and "roles_manage" not in clean.get(actor_role, []):
        return _fail("FORBIDDEN", "You cannot revoke your own role-management access", 403)
    set_setting("role_permissions", clean, "json", "Role capability matrix", session["user_id"])
    return jsonify({"success": True, "message": "Permissions saved", "data": {"permissions": clean}})


@bp.route("/stories", methods=["GET"])
@login_required
@admin_required
@permission_required("stories_admin")
def stories():
    page = max(1, request.args.get("page", 1, type=int))
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
@permission_required("analytics")
def analytics_summary():
    return jsonify({"success": True, "message": "OK", "data": summary(request.args.get("range", 30))})


@bp.route("/analytics/charts", methods=["GET"])
@login_required
@admin_required
@permission_required("analytics")
def analytics_charts():
    key = request.args.get("chart", "")
    return jsonify({"success": True, "message": "OK",
                    "data": chart_data(key, request.args.get("range", 30))})


@bp.route("/analytics/db-health", methods=["GET"])
@login_required
@admin_required
@permission_required("analytics")
def analytics_db_health():
    return jsonify({"success": True, "message": "OK", "data": db_health()})


@bp.route("/analytics/integrity", methods=["GET"])
@login_required
@admin_required
@permission_required("analytics")
def analytics_integrity():
    return jsonify({"success": True, "message": "OK", "data": integrity_check()})


@bp.route("/analytics/recent", methods=["GET"])
@login_required
@admin_required
@permission_required("analytics")
def analytics_recent():
    return jsonify({"success": True, "message": "OK", "data": recent_activity()})


@bp.route("/database/meta", methods=["GET"])
@login_required
@admin_required
@permission_required("database")
def database_meta():
    health = db_health()
    return jsonify({"success": True, "message": "OK", "data": {
        "tables": list(DB_TABLES),
        "counts": health["tables"],
        "size_bytes": health["size_bytes"],
    }})


@bp.route("/database/<table_name>", methods=["GET"])
@login_required
@admin_required
@permission_required("database")
def db_viewer(table_name):
    if table_name not in DB_TABLES:
        return _fail("VALIDATION_ERROR", "Invalid table")
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 25, type=int)))
    q = (request.args.get("q") or "").strip()
    where, args = ["1=1"], []
    if q:
        cols = SEARCH_COLUMNS[table_name]
        where.append("(" + " OR ".join(f"{c} LIKE ?" for c in cols) + ")")
        args += [f"%{q}%"] * len(cols)
    clause = " AND ".join(where)
    total = query_db(f"SELECT COUNT(*) AS c FROM {table_name} WHERE {clause}", tuple(args), one=True)["c"]
    offset = (page - 1) * per_page
    rows = query_db(f"SELECT * FROM {table_name} WHERE {clause} ORDER BY id DESC LIMIT ? OFFSET ?",
                    tuple(args + [per_page, offset]))
    columns = [r["name"] for r in query_db(f"PRAGMA table_info({table_name})")]
    out = []
    for r in rows:
        d = dict(r)
        d.pop("password_hash", None)
        if "setting_value" in d and d.get("is_secret"):
            d["setting_value"] = "••• hidden"
        out.append(d)
    return jsonify({"success": True, "message": "OK", "data": {
        "rows": out, "columns": [c for c in columns if c != "password_hash"],
        "table": table_name, "total": total, "page": page,
        "pages": max(1, (total + per_page - 1) // per_page), "per_page": per_page,
    }})
