from flask import Blueprint, jsonify, session
from app.security import login_required
from app.services.token_service import get_balance, refill_info

bp = Blueprint("wallet", __name__)


@bp.route("", methods=["GET"])
@login_required
def get_wallet():
    info = refill_info(session["user_id"])
    info["token_balance"] = get_balance(session["user_id"])
    return jsonify({"success": True, "message": "OK", "data": info})