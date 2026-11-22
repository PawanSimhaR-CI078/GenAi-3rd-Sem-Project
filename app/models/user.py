import hashlib
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import query_db, execute_db, get_db

ROLE_USER = "USER"
ROLE_ADMIN = "ADMIN"
ROLE_SUPER = "SUPER_ADMIN"
REFILL_HOURS = 48
REFILL_AMOUNT = 5
INITIAL_TOKENS = 5


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_user(username, password, display_name=None, phone_number=None, role="USER", created_by=None):
    ph = generate_password_hash(password)
    ts = now_iso()
    uid = execute_db(
        """INSERT INTO tolstoy_users
        (username, display_name, phone_number, password_hash, role, is_active, token_balance,
         last_token_refill_at, created_by, created_at, updated_by, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (username, display_name, phone_number, ph, role, 1, INITIAL_TOKENS, ts, created_by, ts, created_by, ts),
    )
    return uid


def get_user_by_username(username):
    return query_db("SELECT * FROM tolstoy_users WHERE username=?", (username,), one=True)


def get_user_by_id(uid):
    return query_db("SELECT * FROM tolstoy_users WHERE id=?", (uid,), one=True)


def verify_password(user_row, password):
    return check_password_hash(user_row["password_hash"], password)


def list_users(search=None, role=None, is_active=None, page=1, per_page=20):
    where = ["1=1"]
    args = []
    if search:
        where.append("(username LIKE ? OR display_name LIKE ?)")
        args += [f"%{search}%", f"%{search}%"]
    if role:
        where.append("role=?")
        args.append(role)
    if is_active is not None:
        where.append("is_active=?")
        args.append(1 if is_active else 0)
    offset = (page - 1) * per_page
    sql = f"SELECT id,username,display_name,phone_number,role,is_active,token_balance,last_token_refill_at,created_at,updated_at FROM tolstoy_users WHERE {' AND '.join(where)} ORDER BY id LIMIT ? OFFSET ?"
    args += [per_page, offset]
    return query_db(sql, tuple(args))


def update_user(uid, fields, updated_by):
    allowed = {"display_name", "phone_number", "role", "is_active", "username"}
    sets = []
    args = []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f"{k}=?")
            args.append(v)
    if not sets:
        return
    sets.append("updated_by=?")
    sets.append("updated_at=?")
    args += [updated_by, now_iso(), uid]
    execute_db(f"UPDATE tolstoy_users SET {', '.join(sets)} WHERE id=?", tuple(args))


def update_token_balance(uid, new_balance, updated_by):
    execute_db(
        "UPDATE tolstoy_users SET token_balance=?, updated_by=?, updated_at=? WHERE id=?",
        (new_balance, updated_by, now_iso(), uid),
    )


def adjust_tokens(uid, delta, updated_by):
    # atomic conditional
    db = get_db()
    cur = db.execute(
        "UPDATE tolstoy_users SET token_balance = token_balance + ?, updated_by=?, updated_at=? WHERE id=? AND token_balance + ? >= 0",
        (delta, updated_by, now_iso(), uid, delta),
    )
    db.commit()
    return cur.rowcount > 0


def deduct_tokens(uid, cost, updated_by):
    db = get_db()
    cur = db.execute(
        "UPDATE tolstoy_users SET token_balance = token_balance - ?, updated_by=?, updated_at=? WHERE id=? AND token_balance >= ?",
        (cost, updated_by, now_iso(), uid, cost),
    )
    db.commit()
    return cur.rowcount > 0


def refund_tokens(uid, amount, updated_by):
    if amount <= 0:
        return
    execute_db(
        "UPDATE tolstoy_users SET token_balance = token_balance + ?, updated_by=?, updated_at=? WHERE id=?",
        (amount, updated_by, now_iso(), uid),
    )


def maybe_refill(uid):
    """Apply pending 48h refill(s). Returns new balance. Policy: one refill per call if due (provisional)."""
    row = get_user_by_id(uid)
    if not row:
        return None
    last = datetime.strptime(row["last_token_refill_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if now - last >= timedelta(hours=REFILL_HOURS):
        execute_db(
            "UPDATE tolstoy_users SET token_balance = token_balance + ?, last_token_refill_at = ?, updated_at = ? WHERE id = ?",
            (REFILL_AMOUNT, now_iso(), now_iso(), uid),
        )
        return row["token_balance"] + REFILL_AMOUNT
    return row["token_balance"]


def count_users():
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_users", one=True)
    return r["c"] if r else 0


def count_active_users():
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_users WHERE is_active=1", one=True)
    return r["c"] if r else 0


def get_all_users_for_analytics():
    return query_db("SELECT id, role, is_active, created_at FROM tolstoy_users")