from functools import wraps
from flask import session, jsonify, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Unauthorized", "error": {"code": "UNAUTHORIZED"}}), 401
            return redirect(url_for("public.login_page"))
        return f(*a, **kw)
    return wrapper


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*a, **kw):
            if session.get("role") not in roles:
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
                return redirect(url_for("public.login_page"))
            return f(*a, **kw)
        return wrapper
    return decorator


def admin_required(f):
    return role_required("ADMIN", "SUPER_ADMIN")(f)


def current_user_id():
    return session.get("user_id")


def current_role():
    return session.get("role")