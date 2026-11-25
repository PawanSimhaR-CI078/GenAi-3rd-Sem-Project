from app.db import query_db, execute_db, get_db
from app.models.user import now_iso


def create_story(user_id, title, content, character_gender=None, target_audience=None,
                 desired_length=None, language=None, created_by=None):
    ts = now_iso()
    sid = execute_db(
        """INSERT INTO tolstoy_stories
        (user_id, title, content, character_gender, target_audience, desired_length, language,
         generation_status, story_status, tokens_consumed, created_by, created_at, updated_by, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, title, content, character_gender, target_audience, desired_length, language,
         "pending", "EDITING", 0, created_by if created_by is not None else user_id, ts,
         created_by if created_by is not None else user_id, ts),
    )
    return sid


def get_story(sid):
    return query_db("SELECT * FROM tolstoy_stories WHERE id=?", (sid,), one=True)


def list_stories_for_user(user_id, status=None, page=1, per_page=20, include_deleted=False):
    where = ["user_id=?", "is_deleted=0" if not include_deleted else "1=1"]
    args = [user_id]
    if status:
        where.append("story_status=?")
        args.append(status)
    offset = (page - 1) * per_page
    sql = f"SELECT * FROM tolstoy_stories WHERE {' AND '.join(where)} ORDER BY id DESC LIMIT ? OFFSET ?"
    args += [per_page, offset]
    return query_db(sql, tuple(args))


def list_all_stories(user_id=None, story_status=None, generation_status=None, page=1, per_page=50):
    where = ["is_deleted=0"]
    args = []
    if user_id:
        where.append("user_id=?")
        args.append(user_id)
    if story_status:
        where.append("story_status=?")
        args.append(story_status)
    if generation_status:
        where.append("generation_status=?")
        args.append(generation_status)
    offset = (page - 1) * per_page
    sql = f"SELECT * FROM tolstoy_stories WHERE {' AND '.join(where)} ORDER BY id DESC LIMIT ? OFFSET ?"
    args += [per_page, offset]
    return query_db(sql, tuple(args))


def update_story(sid, fields, updated_by):
    allowed = {"title", "content", "character_gender", "target_audience", "desired_length",
               "language", "generated_script", "generation_status", "story_status",
               "tokens_consumed", "gemini_input_tokens", "gemini_output_tokens",
               "generated_at", "is_deleted"}
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
    args += [updated_by, now_iso(), sid]
    execute_db(f"UPDATE tolstoy_stories SET {', '.join(sets)} WHERE id=?", tuple(args))


def begin_generation(sid, updated_by):
    """Claim a story for generation; fails if another request already claimed it."""
    db = get_db()
    cur = db.execute(
        "UPDATE tolstoy_stories SET generation_status='processing', updated_by=?, updated_at=? WHERE id=? AND is_deleted=0 AND generation_status!='processing'",
        (updated_by, now_iso(), sid),
    )
    db.commit()
    return cur.rowcount > 0


def soft_delete(sid, updated_by):
    execute_db("UPDATE tolstoy_stories SET is_deleted=1, updated_by=?, updated_at=? WHERE id=?",
               (updated_by, now_iso(), sid))


def count_stories():
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_stories WHERE is_deleted=0", one=True)
    return r["c"] if r else 0


def count_by_status(status):
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_stories WHERE story_status=? AND is_deleted=0", (status,), one=True)
    return r["c"] if r else 0


def count_by_gen_status(status):
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_stories WHERE generation_status=? AND is_deleted=0", (status,), one=True)
    return r["c"] if r else 0


def stories_per_day(days=14):
    return query_db(
        """SELECT substr(created_at,1,10) AS d, COUNT(*) AS c
           FROM tolstoy_stories WHERE is_deleted=0
           GROUP BY d ORDER BY d DESC LIMIT ?""", (days,))


def tokens_consumed_total():
    r = query_db("SELECT COALESCE(SUM(tokens_consumed),0) AS s FROM tolstoy_stories", one=True)
    return r["s"] if r else 0


def gemini_usage_totals():
    r = query_db("SELECT COALESCE(SUM(gemini_input_tokens),0) AS i, COALESCE(SUM(gemini_output_tokens),0) AS o FROM tolstoy_stories", one=True)
    return (r["i"], r["o"]) if r else (0, 0)


def top_users_by_stories(limit=5):
    return query_db(
        """SELECT u.username, COUNT(s.id) AS c FROM tolstoy_users u
           LEFT JOIN tolstoy_stories s ON s.user_id=u.id AND s.is_deleted=0
           GROUP BY u.id ORDER BY c DESC LIMIT ?""", (limit,))


def count_deleted():
    r = query_db("SELECT COUNT(*) AS c FROM tolstoy_stories WHERE is_deleted=1", one=True)
    return r["c"] if r else 0


def generation_status_counts():
    return {r["generation_status"]: r["c"] for r in query_db(
        "SELECT generation_status, COUNT(*) AS c FROM tolstoy_stories WHERE is_deleted=0 GROUP BY generation_status")}


def trend_by_day(days, where="1=1"):
    return query_db(
        f"""SELECT substr(created_at,1,10) AS d, COUNT(*) AS c FROM tolstoy_stories
            WHERE is_deleted=0 AND date(created_at) >= date('now', ?) AND {where}
            GROUP BY d ORDER BY d""", (f"-{days} days",))


def tokens_trend(days):
    return query_db(
        """SELECT substr(created_at,1,10) AS d, SUM(tokens_consumed) AS c FROM tolstoy_stories
           WHERE date(created_at) >= date('now', ?) GROUP BY d ORDER BY d""",
        (f"-{days} days",),
    )


def average_stories_per_user():
    r = query_db(
        """SELECT COALESCE(AVG(c),0) AS a FROM (
             SELECT COUNT(s.id) AS c FROM tolstoy_users u
             LEFT JOIN tolstoy_stories s ON s.user_id=u.id AND s.is_deleted=0
             GROUP BY u.id)""", one=True)
    return round(r["a"], 2) if r else 0


def recent_stories(limit=5):
    return query_db(
        """SELECT s.id, s.title, s.story_status, s.generation_status, s.created_at, u.username
           FROM tolstoy_stories s JOIN tolstoy_users u ON u.id=s.user_id
           WHERE s.is_deleted=0 ORDER BY s.id DESC LIMIT ?""", (limit,),
    )