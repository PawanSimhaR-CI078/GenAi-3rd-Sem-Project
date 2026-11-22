from flask import Blueprint, render_template, session, redirect, url_for
from app.security import login_required, admin_required

bp = Blueprint("admin_pages", __name__)


@bp.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html")


@bp.route("/admin/users")
@login_required
@admin_required
def admin_users():
    return render_template("admin/users.html")


@bp.route("/admin/stories")
@login_required
@admin_required
def admin_stories():
    return render_template("admin/stories.html")


@bp.route("/admin/database")
@login_required
@admin_required
def admin_database():
    return render_template("admin/database.html")


@bp.route("/admin/settings")
@login_required
@admin_required
def admin_settings():
    return render_template("admin/settings.html")