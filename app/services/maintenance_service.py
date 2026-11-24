from app.models.system_settings import set_setting, get_setting, maintenance_enabled
from app.models.user import verify_password, get_user_by_id, count_active_users


def toggle(enabled, admin_id, password):
    u = get_user_by_id(admin_id)
    if not u or not verify_password(u, password):
        return False, "Invalid password"
    set_setting("maintenance_mode", bool(enabled), "boolean", "System maintenance flag", updated_by=admin_id)
    return True, "OK"


def is_enabled():
    return maintenance_enabled()


def status():
    row = get_setting("maintenance_mode")
    actor = None
    if row and row["updated_by"]:
        u = get_user_by_id(row["updated_by"])
        actor = u["username"] if u else None
    return {
        "enabled": is_enabled(),
        "updated_at": row["updated_at"] if row else None,
        "updated_by": actor,
        "affected_users": count_active_users(),
    }
