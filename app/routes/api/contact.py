from flask import Blueprint, request, jsonify, session
from app.security import login_required
from app.services.email_service import send_contact_email
from app.schemas.validators import require_fields

bp = Blueprint("contact", __name__)


@bp.route("", methods=["POST"])
@login_required
def contact():
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["subject", "message"])
    if err:
        return jsonify({"success": False, "message": err, "error": {"code": "VALIDATION_ERROR"}}), 400
    ok, msg = send_contact_email(data["subject"], data["message"], session.get("username"))
    if not ok:
        return jsonify({"success": False, "message": msg, "error": {"code": "MAIL_ERROR"}}), 500
    return jsonify({"success": True, "message": "Sent", "data": {}})