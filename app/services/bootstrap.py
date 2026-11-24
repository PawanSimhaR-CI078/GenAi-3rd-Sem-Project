import os
from app.models.user import create_user, get_user_by_username
from app.models.system_settings import ensure_setting
from app.security import DEFAULT_ROLE_PERMISSIONS


def bootstrap():
    ensure_setting("maintenance_mode", False, "boolean", "System maintenance flag")
    ensure_setting("default_token_balance", 5, "integer", "Initial tokens for new users")
    ensure_setting("token_refill_amount", 5, "integer", "Tokens added per refill")
    ensure_setting("token_refill_interval_hours", 48, "integer", "Refill interval")
    ensure_setting("app_name", "TOLSTOY", "string", "Application name")
    ensure_setting("role_permissions", DEFAULT_ROLE_PERMISSIONS, "json", "Role capability matrix")

    pairs = [
        (os.environ.get("ADMIN_USERNAME"), os.environ.get("ADMIN_PASSWORD"), "ADMIN"),
        (os.environ.get("SUPER_ADMIN_USERNAME"), os.environ.get("SUPER_ADMIN_PASSWORD"), "SUPER_ADMIN"),
    ]
    for uname, pw, role in pairs:
        if uname and pw and not get_user_by_username(uname):
            create_user(uname, pw, display_name=uname, role=role, created_by=None)
