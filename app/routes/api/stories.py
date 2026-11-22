from flask import Blueprint, request, jsonify, session
from app.security import login_required
from app.models.story import (create_story, get_story, list_stories_for_user, list_all_stories,
                             update_story, soft_delete)
from app.models.user import get_user_by_id
from app.services.token_service import get_balance, generation_cost, try_deduct, refund
from app.services.gemini_service import generate as gemini_generate, GeminiError
from app.services.maintenance_service import is_enabled
from app.schemas.validators import require_fields

bp = Blueprint("stories", __name__)


def _maintenance_block():
    if is_enabled() and session.get("role") not in ("ADMIN", "SUPER_ADMIN"):
        return jsonify({"success": False, "message": "Maintenance mode", "error": {"code": "MAINTENANCE"}}), 503
    return None


@bp.route("", methods=["GET"])
@login_required
def list_stories():
    b = _maintenance_block()
    if b: return b
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    rows = list_stories_for_user(session["user_id"], status=status, page=page)
    data = [dict(r) for r in rows]
    for d in data:
        d.pop("password_hash", None)
    return jsonify({"success": True, "message": "OK", "data": {"stories": data}})


@bp.route("", methods=["POST"])
@login_required
def create():
    b = _maintenance_block()
    if b: return b
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["title", "content"])
    if err:
        return jsonify({"success": False, "message": err, "error": {"code": "VALIDATION_ERROR"}}), 400
    sid = create_story(
        session["user_id"], data["title"], data["content"],
        data.get("character_gender"), data.get("target_audience"),
        data.get("desired_length"), data.get("language"), created_by=session["user_id"],
    )
    return jsonify({"success": True, "message": "Created", "data": {"story_id": sid}}), 201


@bp.route("/<int:story_id>", methods=["GET"])
@login_required
def get_one(story_id):
    s = get_story(story_id)
    if not s or s["is_deleted"]:
        return jsonify({"success": False, "message": "Not found", "error": {"code": "NOT_FOUND"}}), 404
    if s["user_id"] != session["user_id"] and session.get("role") not in ("ADMIN", "SUPER_ADMIN"):
        return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
    return jsonify({"success": True, "message": "OK", "data": {"story": dict(s)}})


@bp.route("/<int:story_id>", methods=["PATCH"])
@login_required
def update(story_id):
    b = _maintenance_block()
    if b: return b
    s = get_story(story_id)
    if not s or s["is_deleted"]:
        return jsonify({"success": False, "message": "Not found", "error": {"code": "NOT_FOUND"}}), 404
    if s["user_id"] != session["user_id"] and session.get("role") not in ("ADMIN", "SUPER_ADMIN"):
        return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
    data = request.get_json(silent=True) or {}
    update_story(story_id, data, session["user_id"])
    return jsonify({"success": True, "message": "Updated", "data": {}})


@bp.route("/<int:story_id>/generate", methods=["POST"])
@login_required
def generate(story_id):
    b = _maintenance_block()
    if b: return b
    s = get_story(story_id)
    if not s or s["is_deleted"]:
        return jsonify({"success": False, "message": "Not found", "error": {"code": "NOT_FOUND"}}), 404
    if s["user_id"] != session["user_id"]:
        return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
    cost = generation_cost()
    if not try_deduct(session["user_id"], cost, session["user_id"]):
        return jsonify({"success": False, "message": "Insufficient tokens", "error": {"code": "INSUFFICIENT_TOKENS"}}), 402
    update_story(story_id, {"generation_status": "processing"}, session["user_id"])
    try:
        data, in_tok, out_tok = gemini_generate(dict(s))
        update_story(story_id, {
            "generated_script": __import__("json").dumps(data),
            "generation_status": "succeeded",
            "story_status": s["story_status"],
            "tokens_consumed": (s["tokens_consumed"] or 0) + cost,
            "gemini_input_tokens": in_tok,
            "gemini_output_tokens": out_tok,
            "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }, session["user_id"])
        return jsonify({"success": True, "message": "Generated", "data": {
            "story_id": story_id, "generated_script": data,
            "tokens_consumed": cost, "gemini_input_tokens": in_tok, "gemini_output_tokens": out_tok,
        }})
    except GeminiError as e:
        refund(session["user_id"], cost, session["user_id"])
        update_story(story_id, {"generation_status": "failed"}, session["user_id"])
        msg = str(e)
        if "rate" in msg.lower():
            return jsonify({"success": False, "message": msg, "error": {"code": "RATE_LIMITED"}}), 429
        if "timeout" in msg.lower():
            return jsonify({"success": False, "message": msg, "error": {"code": "TIMEOUT"}}), 504
        return jsonify({"success": False, "message": msg, "error": {"code": "PROVIDER_ERROR"}}), 502


@bp.route("/<int:story_id>/regenerate", methods=["POST"])
@login_required
def regenerate(story_id):
    return generate(story_id)


@bp.route("/<int:story_id>/status", methods=["PATCH"])
@login_required
def status(story_id):
    b = _maintenance_block()
    if b: return b
    s = get_story(story_id)
    if not s or s["is_deleted"]:
        return jsonify({"success": False, "message": "Not found", "error": {"code": "NOT_FOUND"}}), 404
    if s["user_id"] != session["user_id"] and session.get("role") not in ("ADMIN", "SUPER_ADMIN"):
        return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
    data = request.get_json(silent=True) or {}
    new = data.get("story_status")
    if new not in ("EDITING", "COMPLETED"):
        return jsonify({"success": False, "message": "Invalid status", "error": {"code": "VALIDATION_ERROR"}}), 400
    update_story(story_id, {"story_status": new}, session["user_id"])
    return jsonify({"success": True, "message": "Updated", "data": {}})


@bp.route("/<int:story_id>", methods=["DELETE"])
@login_required
def delete(story_id):
    s = get_story(story_id)
    if not s or s["is_deleted"]:
        return jsonify({"success": False, "message": "Not found", "error": {"code": "NOT_FOUND"}}), 404
    if s["user_id"] != session["user_id"] and session.get("role") not in ("ADMIN", "SUPER_ADMIN"):
        return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
    soft_delete(story_id, session["user_id"])
    return jsonify({"success": True, "message": "Deleted", "data": {}})