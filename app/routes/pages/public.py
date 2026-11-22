from flask import Blueprint, render_template, session, redirect, url_for
from app.services.maintenance_service import is_enabled

bp = Blueprint("public", __name__)


@bp.route("/")
def index():
    return render_template("public/index.html")


@bp.route("/login")
def login_page():
    return render_template("public/login.html")


@bp.route("/register")
def register_page():
    return render_template("public/register.html")


@bp.route("/admin/login")
def admin_login_page():
    return render_template("public/admin_login.html")


@bp.route("/maintenance")
def maintenance_page():
    return render_template("public/maintenance.html")