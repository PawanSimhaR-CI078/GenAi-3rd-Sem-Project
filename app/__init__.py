import os
import time
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, current_app
from app.config import get_config
from app.extensions import csrf
from app.db import close_db, init_db

_MAINTENANCE_ALLOW = {
    "/maintenance", "/home", "/admin/login", "/api/v1/auth/admin/login",
    "/api/v1/auth/logout", "/api/v1/auth/csrf", "/api/v1/auth/me",
    "/favicon.ico",
}


def _session_guard():
    """Sliding idle timeout: 45 minutes with no request ends the session."""
    if "user_id" not in session:
        return None
    now = int(time.time())
    last = session.get("last_activity")
    if last is not None and now - int(last) > current_app.config["SESSION_IDLE_TIMEOUT"]:
        session.clear()
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Session expired", "error": {"code": "SESSION_EXPIRED"}}), 401
        return redirect(url_for("public.login_page"))
    if not request.path.startswith("/static/"):
        session.permanent = True
        session["last_activity"] = now
    return None


def _global_guards():
    from app.security import sync_session_role
    from app.services.maintenance_service import is_enabled
    expired = _session_guard()
    if expired:
        return expired
    sync_session_role()
    if not is_enabled():
        return None
    p = request.path
    allowed = (
        p.startswith("/static/")
        or p == "/admin"
        or p.startswith("/admin/")
        or p.startswith("/api/v1/admin/")
        or p in _MAINTENANCE_ALLOW
    )
    if allowed:
        return None
    if p.startswith("/api/"):
        return jsonify({"success": False, "message": "System is offline for maintenance", "error": {"code": "MAINTENANCE"}}), 503
    return redirect(url_for("public.maintenance_page"))


def create_app(config_name=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    cfg = get_config(config_name)
    app.config.from_object(cfg)

    app.before_request(_global_guards)
    csrf.init_app(app)
    app.teardown_appcontext(close_db)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        if request.path.startswith("/admin"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

    @app.context_processor
    def admin_context():
        if not request.path.startswith("/admin"):
            return {}
        from app.security import can, ADMIN_CAPABILITIES
        from app.services.maintenance_service import is_enabled
        return {"can": can, "admin_capabilities": ADMIN_CAPABILITIES, "maintenance_on": is_enabled()}

    from app.routes.api.auth import bp as auth_bp
    from app.routes.api.stories import bp as stories_bp
    from app.routes.api.wallet import bp as wallet_bp
    from app.routes.api.admin import bp as admin_bp
    from app.routes.api.system import bp as system_bp
    from app.routes.api.contact import bp as contact_bp
    from app.routes.pages.public import bp as public_bp
    from app.routes.pages.user import bp as user_bp
    from app.routes.pages.admin import bp as admin_pages_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(stories_bp, url_prefix="/api/v1/stories")
    app.register_blueprint(wallet_bp, url_prefix="/api/v1/wallet")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(system_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(contact_bp, url_prefix="/api/v1/contact")
    app.register_blueprint(public_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_pages_bp)

    @app.errorhandler(400)
    def e400(e):
        if _is_api():
            return jsonify({"success": False, "message": "Bad request", "error": {"code": "BAD_REQUEST"}}), 400
        return render_template("errors/400.html"), 400

    @app.errorhandler(401)
    def e401(e):
        if _is_api():
            return jsonify({"success": False, "message": "Unauthorized", "error": {"code": "UNAUTHORIZED"}}), 401
        return render_template("errors/403.html"), 401

    @app.errorhandler(403)
    def e403(e):
        if _is_api():
            return jsonify({"success": False, "message": "Forbidden", "error": {"code": "FORBIDDEN"}}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def e404(e):
        if _is_api():
            return jsonify({"success": False, "message": "Not found", "error": {"code": "NOT_FOUND"}}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def e500(e):
        if _is_api():
            return jsonify({"success": False, "message": "Server error", "error": {"code": "SERVER_ERROR"}}), 500
        return render_template("errors/500.html"), 500

    db_path = app.config["DATABASE_PATH"]
    if db_path == ":memory:":
        init_db(app)
    else:
        full = db_path if os.path.isabs(db_path) else os.path.join(os.path.dirname(app.root_path), db_path)
        if not os.path.exists(full):
            init_db(app)

    with app.app_context():
        from app.services.bootstrap import bootstrap
        bootstrap()

    return app


def _is_api():
    return request.path.startswith("/api/")
