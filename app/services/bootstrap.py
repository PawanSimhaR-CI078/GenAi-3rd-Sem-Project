import os
from app.models.user import create_user, get_user_by_username
from app.models.system_settings import set_setting


def bootstrap():
    set_setting("maintenance_mode", False, "boolean", "System maintenance flag", updated_by=None)
    set_setting("default_token_balance", 5, "integer", "Initial tokens for new users", updated_by=None)
    set_setting("token_refill_amount", 5, "integer", "Tokens added per refill", updated_by=None)
    set_setting("token_refill_interval_hours", 48, "integer", "Refill interval", updated_by=None)
    set_setting("app_name", "TOLSTOY", "string", "Application name", updated_by=None)

    # Admin accounts are created only from explicit environment variables (no hardcoded credentials).
    pairs = [
        (os.environ.get("ADMIN_USERNAME"), os.environ.get("ADMIN_PASSWORD"), "ADMIN"),
        (os.environ.get("SUPER_ADMIN_USERNAME"), os.environ.get("SUPER_ADMIN_PASSWORD"), "SUPER_ADMIN"),
    ]
    for uname, pw, role in pairs:
        if uname and pw and not get_user_by_username(uname):
            create_user(uname, pw, display_name=uname, role=role, created_by=None)