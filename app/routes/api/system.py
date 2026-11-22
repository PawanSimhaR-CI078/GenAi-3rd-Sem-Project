from flask import Blueprint, request, jsonify, session
from app.security import login_required, admin_required
from app.models.system_settings import list_settings, set_setting, get_setting_value
from app.services.maintenance_service import toggle, is_enabled

bp = Blueprint("system", __name__)


@bp.route("/settings", methods=["GET"])
@login_required
@admin_required
def get_settings():
    rows = list_settings()
    return jsonify({"success": True, "message": "OK", "data": {"settings": [dict(r) for r in rows]}})


@bp.route("/settings", methods=["PATCH"])
@login_required
@admin_required
def patch_setting():
    data = request.get_json(silent=True) or {}
    key = data.get("setting_key")
    if not key:
        return jsonify({"success": False, "message": "Missing key", "error": {"code": "VALIDATION_ERROR"}}), 400
    set_setting(key, data.get("setting_value"), data.get("value_type", "string"), data.get("description"), session["user_id"])
    return jsonify({"success": True, "message": "Updated", "data": {}})


@bp.route("/maintenance", methods=["PATCH"])
@login_required
@admin_required
def maintenance():
    data = request.get_json(silent=True) or {}
    ok, msg = toggle(bool(data.get("enabled")), session["user_id"], data.get("password", ""))
    if not ok:
        return jsonify({"success": False, "message": msg, "error": {"code": "UNAUTHORIZED"}}), 401
    return jsonify({"success": True, "message": "Updated", "data": {"enabled": is_enabled()}})