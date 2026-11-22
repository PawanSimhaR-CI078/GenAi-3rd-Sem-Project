from app.models.system_settings import set_setting, maintenance_enabled
from app.models.user import verify_password, get_user_by_id


def toggle(enabled, admin_id, password):
    u = get_user_by_id(admin_id)
    if not u or not verify_password(u, password):
        return False, "Invalid password"
    set_setting("maintenance_mode", bool(enabled), "boolean", "System maintenance flag", updated_by=admin_id)
    return True, "OK"


def is_enabled():
    return maintenance_enabled()