from flask import Blueprint, render_template, session, redirect, url_for
from app.security import login_required
from app.services.maintenance_service import is_enabled

bp = Blueprint("user_pages", __name__)


def _guard():
    if is_enabled() and session.get("role") not in ("ADMIN", "SUPER_ADMIN"):
        return True
    return False


@bp.route("/dashboard")
@login_required
def dashboard():
    if _guard(): return redirect(url_for("public.maintenance_page"))
    return render_template("user/dashboard.html")


@bp.route("/stories")
@login_required
def stories_page():
    if _guard(): return redirect(url_for("public.maintenance_page"))
    return render_template("user/stories.html")


@bp.route("/stories/new")
@login_required
def create_story_page():
    if _guard(): return redirect(url_for("public.maintenance_page"))
    return render_template("user/create_story.html")


@bp.route("/stories/<int:story_id>")
@login_required
def story_editor_page(story_id):
    if _guard(): return redirect(url_for("public.maintenance_page"))
    return render_template("user/story_editor.html", story_id=story_id)


@bp.route("/wallet")
@login_required
def wallet_page():
    if _guard(): return redirect(url_for("public.maintenance_page"))
    return render_template("user/wallet.html")


@bp.route("/contact")
@login_required
def contact_page():
    if _guard(): return redirect(url_for("public.maintenance_page"))
    return render_template("user/contact.html")


@bp.route("/profile")
@login_required
def profile_page():
    return render_template("user/profile.html")