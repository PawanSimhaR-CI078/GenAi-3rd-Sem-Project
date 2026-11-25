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


def update_user(uid, fields, updated_by, keep_last_super=False):
    allowed = {"display_name", "phone_number", "role", "is_active", "username"}
    sets = []
    args = []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f"{k}=?")
            args.append(v)
    if not sets:
        return True
    db = get_db()
    db.execute("BEGIN IMMEDIATE")
    try:
        if keep_last_super:
            row = db.execute("SELECT role, is_active FROM tolstoy_users WHERE id=?", (uid,)).fetchone()
            new_role = fields.get("role", row["role"] if row else None)
            new_active = fields.get("is_active", row["is_active"] if row else None)
            if row and row["role"] == ROLE_SUPER and row["is_active"] and (new_role != ROLE_SUPER or not new_active):
                remaining = db.execute(
                    "SELECT COUNT(*) AS c FROM tolstoy_users WHERE role=? AND is_active=1 AND id!=?",
                    (ROLE_SUPER, uid),
                ).fetchone()["c"]
                if remaining == 0:
                    db.rollback()
                    return False
        sets += ["updated_by=?", "updated_at=?"]
        args += [updated_by, now_iso(), uid]
        db.execute(f"UPDATE tolstoy_users SET {', '.join(sets)} WHERE id=?", tuple(args))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def update_token_balance(uid, new_balance, updated_by):
    execute_db(
        "UPDATE tolstoy_users SET token_balance=?, updated_by=?, updated_at=? WHERE id=?",
        (new_balance, updated_by, now_iso(), uid),
    )


def adjust_tokens(uid, delta, updated_by):
    # atomic conditional; admin adjustments are increases only
    if delta <= 0:
        return False
    db = get_db()
    cur = db.execute(
        "UPDATE tolstoy_users SET token_balance = token_balance + ?, updated_by=?, updated_at=? WHERE id=? AND token_balance + ? >= 0",
        (delta, updated_by, now_iso(), uid, delta),
    )
    db.commit()
    return cur.rowcount > 0


def deduct_tokens(uid, cost, updated_by):
    if cost <= 0:
        return False
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
        ts = now_iso()
        db = get_db()
        cur = db.execute(
            "UPDATE tolstoy_users SET token_balance = token_balance + ?, last_token_refill_at = ?, updated_at = ? WHERE id = ? AND last_token_refill_at = ?",
            (REFILL_AMOUNT, ts, ts, uid, row["last_token_refill_at"]),
        )
        db.commit()
        if cur.rowcount:
            return row["token_balance"] + REFILL_AMOUNT
        updated = get_user_by_id(uid)
        return updated["token_balance"] if updated else None
    return row["token_balance"]


def count_users():
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_users", one=True)
    return r["c"] if r else 0


def count_active_users():
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_users WHERE is_active=1", one=True)
    return r["c"] if r else 0


def get_all_users_for_analytics():
    return query_db("SELECT id, role, is_active, created_at FROM tolstoy_users")


def count_by_role(role):
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_users WHERE role=?", (role,), one=True)
    return r["c"] if r else 0


def role_counts():
    return {r["role"]: r["c"] for r in query_db("SELECT role, COUNT(*) AS c FROM tolstoy_users GROUP BY role")}


def registration_trend(days):
    return query_db(
        """SELECT substr(created_at,1,10) AS d, COUNT(*) AS c FROM tolstoy_users
           WHERE date(created_at) >= date('now', ?) GROUP BY d ORDER BY d""",
        (f"-{days} days",),
    )


def token_totals():
    r = query_db(
        """SELECT COALESCE(SUM(token_balance),0) AS total,
                  COALESCE(AVG(token_balance),0) AS average,
                  COALESCE(SUM(CASE WHEN token_balance <= 2 THEN 1 ELSE 0 END),0) AS low
           FROM tolstoy_users""", one=True)
    return {"total": r["total"], "average": round(r["average"], 2), "low": r["low"]}


def token_balance_buckets():
    rows = query_db(
        """SELECT CASE
             WHEN token_balance = 0 THEN '0'
             WHEN token_balance BETWEEN 1 AND 5 THEN '1-5'
             WHEN token_balance BETWEEN 6 AND 20 THEN '6-20'
             ELSE '21+' END AS bucket, COUNT(*) AS c
           FROM tolstoy_users GROUP BY bucket ORDER BY MIN(token_balance)"""
    )
    return [{"label": r["bucket"], "count": r["c"]} for r in rows]


def recent_users(limit=5):
    return query_db(
        "SELECT id, username, role, is_active, token_balance, created_at FROM tolstoy_users ORDER BY id DESC LIMIT ?",
        (limit,),
    )