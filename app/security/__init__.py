from functools import wraps
from flask import session, jsonify, request, redirect, url_for, g, render_template

USER_CAPABILITIES = {
    "dashboard": "User dashboard",
    "stories": "My stories",
    "wallet": "Token wallet",
    "contact": "Contact admin",
    "profile": "Profile",
}

ADMIN_CAPABILITIES = {
    "analytics": "Analytics dashboard",
    "users_view": "View users",
    "users_edit": "Edit user details",
    "wallet_edit": "Edit token wallet",
    "roles_view": "View role access",
    "roles_manage": "Manage roles and permissions",
    "database": "Live database",
    "stories_admin": "Manage stories",
    "settings": "System settings",
    "system": "System offline control",
}

ALL_CAPABILITIES = {**USER_CAPABILITIES, **ADMIN_CAPABILITIES}

# These can never be granted to USER or ADMIN, even through the matrix.
SUPER_ONLY_CAPABILITIES = {
    "wallet_edit", "roles_view", "roles_manage", "settings", "system",
}

DEFAULT_ROLE_PERMISSIONS = {
    "USER": list(USER_CAPABILITIES),
    "ADMIN": [k for k in ADMIN_CAPABILITIES if k not in SUPER_ONLY_CAPABILITIES],
    "SUPER_ADMIN": ["*"],
}

VALID_ROLES = ("USER", "ADMIN", "SUPER_ADMIN")
MANAGEABLE_CAPABILITIES = [k for k in ADMIN_CAPABILITIES if k not in SUPER_ONLY_CAPABILITIES]


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Unauthorized", "error": {"code": "UNAUTHORIZED"}}), 401
            return redirect(url_for("public.login_page"))
        return f(*a, **kw)
    return wrapper


def _forbidden():
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
    return render_template("errors/403.html"), 403


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*a, **kw):
            if session.get("role") not in roles:
                return _forbidden()
            return f(*a, **kw)
        return wrapper
    return decorator


def admin_required(f):
    return role_required("ADMIN", "SUPER_ADMIN")(f)


def sync_session_role():
    """Re-read role/status from DB so role changes take effect immediately."""
    if "user_id" not in session:
        return
    from app.models.user import get_user_by_id
    u = get_user_by_id(session["user_id"])
    if not u or not u["is_active"]:
        session.clear()
        return
    session["role"] = u["role"]
    session["username"] = u["username"]


def permissions_for(role=None):
    from app.models.system_settings import get_setting_value
    role = role or session.get("role")
    cache = getattr(g, "_role_permissions", None)
    if cache is None:
        cache = g._role_permissions = {}
    if role not in cache:
        if role == "SUPER_ADMIN":
            cache[role] = set(ALL_CAPABILITIES)
        else:
            stored = get_setting_value("role_permissions", DEFAULT_ROLE_PERMISSIONS) or {}
            value = stored.get(role, [])
            granted = set(value) if isinstance(value, list) else set()
            cache[role] = granted - SUPER_ONLY_CAPABILITIES
    return cache[role]


def can(capability):
    return capability in permissions_for()


def permission_required(capability):
    def decorator(f):
        @wraps(f)
        def wrapper(*a, **kw):
            if not can(capability):
                return _forbidden()
            return f(*a, **kw)
        return wrapper
    return decorator


def current_user_id():
    return session.get("user_id")


def current_role():
    return session.get("role")
