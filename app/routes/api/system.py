from flask import Blueprint, request, jsonify, session
from app.security import login_required, admin_required, permission_required
from app.models.system_settings import list_settings, set_setting, get_setting_value
from app.services.maintenance_service import toggle, is_enabled, status

bp = Blueprint("system", __name__)

# Structured/internal settings are managed by their own screens, not this key/value list.
INTERNAL_SETTINGS = {"role_permissions", "maintenance_mode"}
WRITABLE_SETTINGS = {
    "app_name": "string",
    "default_token_balance": "integer",
    "token_refill_amount": "integer",
    "token_refill_interval_hours": "integer",
    "token_cost_per_generation": "integer",
}


@bp.route("/settings", methods=["GET"])
@login_required
@admin_required
@permission_required("settings")
def get_settings():
    rows = [dict(r) for r in list_settings() if r["setting_key"] not in INTERNAL_SETTINGS]
    return jsonify({"success": True, "message": "OK", "data": {"settings": rows}})


@bp.route("/settings", methods=["PATCH"])
@login_required
@admin_required
@permission_required("settings")
def patch_setting():
    data = request.get_json(silent=True) or {}
    key = data.get("setting_key")
    expected_type = WRITABLE_SETTINGS.get(key)
    if not expected_type:
        return jsonify({"success": False, "message": "Setting cannot be changed here", "error": {"code": "VALIDATION_ERROR"}}), 400
    value = data.get("setting_value")
    if expected_type == "integer":
        if isinstance(value, bool) or not str(value).lstrip("-").isdigit() or int(value) <= 0:
            return jsonify({"success": False, "message": "Value must be a positive integer", "error": {"code": "VALIDATION_ERROR"}}), 400
        value = int(value)
    elif not isinstance(value, str) or len(value) > 200:
        return jsonify({"success": False, "message": "Invalid value", "error": {"code": "VALIDATION_ERROR"}}), 400
    set_setting(key, value, expected_type, data.get("description"), session["user_id"])
    return jsonify({"success": True, "message": "Updated", "data": {}})


@bp.route("/system/status", methods=["GET"])
@login_required
@admin_required
@permission_required("system")
def system_status():
    return jsonify({"success": True, "message": "OK", "data": status()})


@bp.route("/maintenance", methods=["PATCH"])
@login_required
@admin_required
@permission_required("system")
def maintenance():
    data = request.get_json(silent=True) or {}
    enabled = data.get("enabled")
    if not isinstance(enabled, bool):
        return jsonify({"success": False, "message": "enabled must be a boolean", "error": {"code": "VALIDATION_ERROR"}}), 400
    ok, msg = toggle(enabled, session["user_id"], data.get("password", ""))
    if not ok:
        return jsonify({"success": False, "message": msg, "error": {"code": "UNAUTHORIZED"}}), 401
    return jsonify({"success": True, "message": "Updated", "data": {"enabled": is_enabled()}})