"""One-shot dummy-data refresh for analytics demos. Refuses to run twice."""
import json
import secrets
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from werkzeug.security import generate_password_hash

DB = Path("database/tolstoy.db")
BACKUP_DIR = Path("C:/Users/PawanSimha/AppData/Local/Temp/opencode")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc)
NOW = now.strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY = now.date()
DAYS = [TODAY - timedelta(days=13 - i) for i in range(14)]

REAL_IDS = (307, 308, 309)
PATTERN = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40]
INACTIVE_EXISTING = {311, 318, 327, 340, 352, 363}
USER_DAY_COUNTS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 10, 9, 7, 5, 1]
assert sum(USER_DAY_COUNTS) == 95
DAY_POOL = [d for d, c in enumerate(USER_DAY_COUNTS) for _ in range(c)]

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
con.execute("PRAGMA foreign_keys=ON")

if con.execute("SELECT COUNT(*) FROM tolstoy_users WHERE username LIKE 'demo_%'").fetchone()[0]:
    raise SystemExit("Already seeded; refusing to double-seed")

shutil.copy2(DB, BACKUP_DIR / f"tolstoy_backup_{now:%Y%m%d_%H%M%S}.db")

con.execute("BEGIN IMMEDIATE")
try:
    dummy = con.execute(
        "SELECT id FROM tolstoy_users WHERE id NOT IN (?,?,?) ORDER BY id", REAL_IDS
    ).fetchall()
    assert len(dummy) == len(DAY_POOL)

    for i, row in enumerate(dummy):
        day = DAYS[DAY_POOL[i]]
        con.execute(
            """UPDATE tolstoy_users
               SET created_at=?, last_token_refill_at=?, is_active=?, token_balance=?,
                   updated_by=?, updated_at=? WHERE id=?""",
            (f"{day}T08:00:00Z", f"{TODAY}T12:00:00Z",
             0 if row["id"] in INACTIVE_EXISTING else 1,
             PATTERN[i % len(PATTERN)], 307, NOW, row["id"]),
        )

    next_uid = con.execute("SELECT COALESCE(MAX(id),0)+1 FROM tolstoy_users").fetchone()[0]
    new_user_ids = []
    i = 0

    def put_user(username, role, active):
        global next_uid
        uid = next_uid
        next_uid += 1
        day = DAYS[i % 14]
        pw = generate_password_hash(secrets.token_urlsafe(24))  # plaintext discarded
        con.execute(
            """INSERT INTO tolstoy_users
               (username,display_name,phone_number,password_hash,role,is_active,
                token_balance,last_token_refill_at,created_by,created_at,
                updated_by,updated_at,reserved_slot_1,reserved_slot_2)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (username, username.replace("_", " ").title(), None, pw, role,
             1 if active else 0, PATTERN[(len(dummy) + i) % len(PATTERN)],
             f"{TODAY}T12:00:00Z", 307, f"{day}T08:00:00Z",
             307, NOW, None, None),
        )
        return uid

    for k in range(19):
        new_user_ids.append(put_user(f"demo_user_{k+1:02d}", "USER", k < 17))
        i += 1
    for k in range(3):
        put_user(f"demo_admin_{k+1:02d}", "ADMIN", False)
        i += 1
    put_user("demo_super_01", "SUPER_ADMIN", False)

    live = con.execute(
        "SELECT id, generation_status FROM tolstoy_stories WHERE is_deleted=0 ORDER BY id"
    ).fetchall()
    n = len(live)

    for k, row in enumerate(live):
        di = min(13, int(14 * ((k + 1) / n) ** 0.6))
        day = DAYS[di]
        if row["generation_status"] == "succeeded":
            con.execute(
                """UPDATE tolstoy_stories
                   SET created_at=?, updated_at=?, updated_by=?,
                       story_status=CASE WHEN id%5<>0 THEN 'COMPLETED' ELSE story_status END,
                       tokens_consumed=?, gemini_input_tokens=?, gemini_output_tokens=?,
                       generated_at=? WHERE id=?""",
                (f"{day}T10:00:00Z", NOW, 307, 1 + di // 3,
                 180 + 40 * di, 320 + 90 * di, f"{day}T10:05:00Z", row["id"]),
            )
        else:
            con.execute(
                """UPDATE tolstoy_stories
                   SET created_at=?, updated_at=?, updated_by=?, tokens_consumed=0,
                       gemini_input_tokens=NULL, gemini_output_tokens=NULL,
                       generated_at=NULL, generated_script=NULL WHERE id=?""",
                (f"{day}T10:00:00Z", NOW, 307, row["id"]),
            )

    counts = {r["user_id"]: r["c"] for r in con.execute(
        "SELECT user_id, COUNT(*) c FROM tolstoy_stories WHERE is_deleted=0 GROUP BY user_id")}
    targets = {310: 12, 321: 10, 322: 9, 326: 8, 328: 7, 332: 6, 335: 5, 337: 5}

    next_sid = con.execute("SELECT COALESCE(MAX(id),0)+1 FROM tolstoy_stories").fetchone()[0]
    state = [next_sid, 0]
    rows = []

    def add_story(uid):
        sid, j = state
        di = j % 14
        day = DAYS[di]
        gen = ("succeeded", "succeeded", "failed", "pending")[j % 4]
        ok = gen == "succeeded"
        title = f"Demo Comic Script {sid}"
        script = json.dumps({
            "title": title,
            "scenes": [{"scene_number": 1, "setting": "A quiet street", "panels": [{
                "panel_number": 1,
                "description": "A hero decides to help a stranger.",
                "characters": ["Hero"],
                "dialogue": [{"character": "Hero", "line": "Let's begin."}],
                "narration": "The story starts here.",
            }]}],
        }) if ok else None
        rows.append((
            uid, title, "Dummy story seeded for analytics.",
            ("female", "male", "non-binary")[j % 3],
            ("children", "teens", "adults", "all ages")[j % 4],
            ("short", "medium", "long")[j % 3],
            ("English", "Hindi", "Spanish")[j % 3],
            script, gen, "COMPLETED" if ok or j % 8 == 2 else "EDITING",
            (1 + di // 3) if ok else 0,
            (180 + 40 * di) if ok else None,
            (320 + 90 * di) if ok else None,
            f"{day}T10:05:00Z" if ok else None,
            0, uid, f"{day}T10:00:00Z", uid, NOW, None, None,
        ))
        state[0] += 1
        state[1] += 1

    for uid, target in targets.items():
        for _ in range(target - counts.get(uid, 0)):
            add_story(uid)
    for uid in new_user_ids:
        add_story(uid)

    con.executemany(
        """INSERT INTO tolstoy_stories
           (user_id,title,content,character_gender,target_audience,desired_length,
            language,generated_script,generation_status,story_status,tokens_consumed,
            gemini_input_tokens,gemini_output_tokens,generated_at,is_deleted,
            created_by,created_at,updated_by,updated_at,reserved_slot_1,reserved_slot_2)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    con.commit()
except Exception:
    con.rollback()
    raise
finally:
    con.close()

print(f"Seeded {len(new_user_ids)} users and {len(rows)} stories. Backup in {BACKUP_DIR}")
