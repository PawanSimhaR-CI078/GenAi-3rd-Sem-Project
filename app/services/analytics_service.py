from app.models.user import count_users, count_active_users
from app.models.story import (count_stories, count_by_status, count_by_gen_status,
                             tokens_consumed_total, gemini_usage_totals, top_users_by_stories,
                             stories_per_day)


def summary():
    gi, go = gemini_usage_totals()
    return {
        "total_users": count_users(),
        "active_users": count_active_users(),
        "total_stories": count_stories(),
        "editing_stories": count_by_status("EDITING"),
        "completed_stories": count_by_status("COMPLETED"),
        "tokens_consumed": tokens_consumed_total(),
        "gemini_input_tokens": gi,
        "gemini_output_tokens": go,
        "generation_succeeded": count_by_gen_status("succeeded"),
        "generation_failed": count_by_gen_status("failed"),
    }


def chart_data(key):
    if key == "users_status":
        return {"labels": ["Active", "Inactive"],
                "data": [count_active_users(), count_users() - count_active_users()]}
    if key == "stories_status":
        return {"labels": ["Editing", "Completed"],
                "data": [count_by_status("EDITING"), count_by_status("COMPLETED")]}
    if key == "stories_per_day":
        rows = stories_per_day(14)
        rows = list(reversed(rows))
        return {"labels": [r["d"] for r in rows], "data": [r["c"] for r in rows]}
    if key == "top_users":
        rows = top_users_by_stories(5)
        return {"labels": [r["username"] for r in rows], "data": [r["c"] for r in rows]}
    if key == "gemini_usage":
        gi, go = gemini_usage_totals()
        return {"labels": ["Input", "Output"], "data": [gi, go]}
    if key == "tokens_consumed":
        return {"labels": ["Consumed"], "data": [tokens_consumed_total()]}
    return {"labels": [], "data": []}