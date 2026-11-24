from app.db import query_db
from app.models.user import (count_users, count_active_users, count_by_role, role_counts,
                             registration_trend, token_totals, token_balance_buckets,
                             recent_users)
from app.models.story import (count_stories, count_by_status, count_by_gen_status,
                              tokens_consumed_total, gemini_usage_totals, top_users_by_stories,
                              stories_per_day, count_deleted, generation_status_counts,
                              trend_by_day, tokens_trend, average_stories_per_user,
                              recent_stories)

TABLES = ("tolstoy_users", "tolstoy_stories", "tolstoy_system_settings")


def _days(value):
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = 30
    return n if 0 < n <= 36500 else 30


def summary(range_days=30):
    days = _days(range_days)
    gi, go = gemini_usage_totals()
    tokens = token_totals()
    gen = generation_status_counts()
    return {
        "users": {
            "total": count_users(),
            "active": count_active_users(),
            "inactive": count_users() - count_active_users(),
            "by_role": role_counts(),
            "new_in_range": sum(r["c"] for r in registration_trend(days)),
        },
        "stories": {
            "total": count_stories(),
            "editing": count_by_status("EDITING"),
            "completed": count_by_status("COMPLETED"),
            "deleted": count_deleted(),
            "average_per_user": average_stories_per_user(),
            "by_generation": gen,
            "success_rate": round(100.0 * gen.get("succeeded", 0) / max(1, count_stories()), 1),
            "new_in_range": sum(r["c"] for r in trend_by_day(days)),
        },
        "tokens": {
            "in_circulation": tokens["total"],
            "average_balance": tokens["average"],
            "low_balance_users": tokens["low"],
            "consumed": tokens_consumed_total(),
            "gemini_input": gi,
            "gemini_output": go,
            "consumed_in_range": sum(r["c"] or 0 for r in tokens_trend(days)),
        },
        "system": {
            "maintenance_settings": 1,
            "range_days": days,
        },
    }


def chart_data(key, range_days=30):
    days = _days(range_days)
    if key == "users_growth":
        rows = registration_trend(days)
        return {"labels": [r["d"] for r in rows], "data": [r["c"] for r in rows]}
    if key == "users_role":
        rows = role_counts()
        return {"labels": list(rows), "data": [rows[k] for k in rows]}
    if key == "token_distribution":
        rows = token_balance_buckets()
        return {"labels": [r["label"] for r in rows], "data": [r["count"] for r in rows]}
    if key == "stories_status":
        return {"labels": ["Editing", "Completed"],
                "data": [count_by_status("EDITING"), count_by_status("COMPLETED")]}
    if key == "generation_status":
        rows = generation_status_counts()
        return {"labels": list(rows), "data": [rows[k] for k in rows]}
    if key == "stories_per_day":
        rows = trend_by_day(days)
        return {"labels": [r["d"] for r in rows], "data": [r["c"] for r in rows]}
    if key == "tokens_per_day":
        rows = tokens_trend(days)
        return {"labels": [r["d"] for r in rows], "data": [r["c"] or 0 for r in rows]}
    if key == "gemini_usage":
        gi, go = gemini_usage_totals()
        return {"labels": ["Input", "Output"], "data": [gi, go]}
    if key == "top_users":
        rows = top_users_by_stories(8)
        return {"labels": [r["username"] for r in rows], "data": [r["c"] for r in rows]}
    return {"labels": [], "data": []}


def db_health():
    counts = {}
    last = {}
    for table in TABLES:
        counts[table] = query_db(f"SELECT COUNT(*) AS c FROM {table}", one=True)["c"]
        row = query_db(f"SELECT MAX(updated_at) AS u FROM {table}", one=True)
        last[table] = row["u"] if row else None
    page = query_db("PRAGMA page_count", one=True)
    size = query_db("PRAGMA page_size", one=True)
    return {
        "tables": counts,
        "last_updated": last,
        "size_bytes": (page["page_count"] * size["page_size"]) if page and size else 0,
    }


def integrity_check():
    result = query_db("PRAGMA integrity_check", one=True)
    fk = query_db("PRAGMA foreign_key_check")
    return {
        "integrity": result["integrity_check"] if result else "unknown",
        "foreign_key_violations": len(fk),
    }


def recent_activity():
    return {
        "users": [dict(r) for r in recent_users()],
        "stories": [dict(r) for r in recent_stories()],
    }
