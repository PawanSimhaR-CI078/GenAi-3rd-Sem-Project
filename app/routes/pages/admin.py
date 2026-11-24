from flask import Blueprint, render_template
from app.security import login_required, admin_required, permission_required

bp = Blueprint("admin_pages", __name__)


@bp.route("/admin")
@login_required
@admin_required
@permission_required("analytics")
def admin_dashboard():
    return render_template("admin/dashboard.html")


@bp.route("/admin/users")
@login_required
@admin_required
@permission_required("users_view")
def admin_users():
    return render_template("admin/users.html")


@bp.route("/admin/roles")
@login_required
@admin_required
@permission_required("roles_view")
def admin_roles():
    return render_template("admin/roles.html")


@bp.route("/admin/assign-roles")
@login_required
@admin_required
@permission_required("roles_manage")
def admin_assign_roles():
    return render_template("admin/assign_roles.html")


@bp.route("/admin/stories")
@login_required
@admin_required
@permission_required("stories_admin")
def admin_stories():
    return render_template("admin/stories.html")


@bp.route("/admin/database")
@login_required
@admin_required
@permission_required("database")
def admin_database():
    return render_template("admin/database.html")


@bp.route("/admin/settings")
@login_required
@admin_required
@permission_required("settings")
def admin_settings():
    return render_template("admin/settings.html")


@bp.route("/admin/system")
@login_required
@admin_required
@permission_required("system")
def admin_system():
    return render_template("admin/system.html")
