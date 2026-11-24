from app.db import query_db, execute_db
from app.models.user import now_iso


def get_setting(key):
    return query_db("SELECT * FROM tolstoy_system_settings WHERE setting_key=?", (key,), one=True)


def get_setting_value(key, default=None):
    row = get_setting(key)
    if not row:
        return default
    v = row["setting_value"]
    t = row["value_type"]
    if t == "integer":
        return int(v)
    if t == "boolean":
        return v.lower() in ("true", "1", "yes")
    if t == "json":
        import json
        return json.loads(v)
    return v


def set_setting(key, value, value_type="string", description=None, updated_by=None):
    existing = get_setting(key)
    ts = now_iso()
    v = value if not isinstance(value, bool) else ("true" if value else "false")
    if isinstance(value, (dict, list)):
        import json
        v = json.dumps(value)
        value_type = "json"
    if existing:
        execute_db(
            "UPDATE tolstoy_system_settings SET setting_value=?, value_type=?, description=COALESCE(?,description), updated_by=?, updated_at=? WHERE setting_key=?",
            (str(v), value_type, description, updated_by, ts, key),
        )
    else:
        execute_db(
            "INSERT INTO tolstoy_system_settings (setting_key, setting_value, value_type, description, created_by, created_at, updated_by, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (key, str(v), value_type, description, updated_by, ts, updated_by, ts),
        )


def ensure_setting(key, value, value_type="string", description=None, updated_by=None):
    if not get_setting(key):
        set_setting(key, value, value_type, description, updated_by)


def list_settings():
    return query_db("SELECT * FROM tolstoy_system_settings ORDER BY setting_key")


def maintenance_enabled():
    return bool(get_setting_value("maintenance_mode", False))