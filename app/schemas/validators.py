import re

def require_fields(data, fields):
    if not isinstance(data, dict):
        return "Invalid JSON body"
    for f in fields:
        if data.get(f) in (None, ""):
            return f"Missing field: {f}"
    return None

def validate_username(u):
    return bool(u) and len(u) >= 3 and len(u) <= 40 and re.match(r"^[A-Za-z0-9_.-]+$", u)

def validate_password(p):
    return bool(p) and len(p) >= 8

def validate_email(s):
    return bool(s) and "@" in s and "." in s.split("@")[-1]