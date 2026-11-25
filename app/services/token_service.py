from datetime import datetime, timedelta, timezone
from app.models.user import (maybe_refill, deduct_tokens, refund_tokens, get_user_by_id,
                            REFILL_AMOUNT, REFILL_HOURS)
from app.models.system_settings import get_setting_value


def get_balance(uid):
    maybe_refill(uid)
    u = get_user_by_id(uid)
    return u["token_balance"] if u else 0


def token_cost():
    try:
        cost = int(get_setting_value("token_cost_per_generation", 1))
    except (TypeError, ValueError):
        return 1
    return max(1, cost)


def generation_cost():
    return token_cost()


def try_deduct(uid, cost, updated_by):
    if cost <= 0:
        return False
    maybe_refill(uid)
    return deduct_tokens(uid, cost, updated_by)


def refund(uid, amount, updated_by):
    refund_tokens(uid, amount, updated_by)


def refill_info(uid):
    u = get_user_by_id(uid)
    if not u:
        return None
    last = datetime.strptime(u["last_token_refill_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return {
        "token_balance": u["token_balance"],
        "last_token_refill_at": u["last_token_refill_at"],
        "next_refill_at": (last + timedelta(hours=REFILL_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "refill_amount": REFILL_AMOUNT,
        "refill_interval_hours": REFILL_HOURS,
    }