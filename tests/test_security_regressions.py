from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app import create_app
from app.db import get_db
from app.models.story import create_story, get_story
from app.models.system_settings import set_setting
from app.models.user import create_user, get_user_by_id, maybe_refill, update_user, now_iso
from app.routes.api import stories as stories_route
from app.services import gemini_service
from app.services.token_service import generation_cost, try_deduct

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ctx(client):
    return client.application.app_context()


def _make_user(ctx, name, role="USER", password="password123"):
    with ctx:
        return create_user(name, password, display_name=name, role=role)


def _login(client, uid, role):
    with client.session_transaction() as s:
        s["user_id"] = uid
        s["role"] = role
        s["username"] = "tester"


def test_csrf_blocks_tokenless_state_change():
    app = create_app("testing")
    app.config["WTF_CSRF_ENABLED"] = True
    with app.test_client() as c:
        assert c.post("/api/v1/auth/logout").status_code == 400


def test_settings_patch_rejects_internal_and_secret_keys(client, ctx):
    admin = _make_user(ctx, "settings_guard", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")
    for key in ("maintenance_mode", "role_permissions", "secret_key", "unknown"):
        r = client.patch("/api/v1/admin/settings", json={"setting_key": key, "setting_value": "true"})
        assert r.status_code == 400, key
    r = client.patch("/api/v1/admin/settings", json={"setting_key": "token_cost_per_generation", "setting_value": -5})
    assert r.status_code == 400
    assert client.patch("/api/v1/admin/maintenance", json={"enabled": "false", "password": "password123"}).status_code == 400


def test_story_patch_cannot_write_internal_fields_and_bad_page_is_safe(client, ctx):
    uid = _make_user(ctx, "story_owner")
    with ctx:
        sid = create_story(uid, "Original", "Content")
    _login(client, uid, "USER")
    r = client.patch(f"/api/v1/stories/{sid}", json={
        "title": "Updated", "generation_status": "succeeded", "tokens_consumed": 999, "is_deleted": 1,
    })
    assert r.status_code == 200
    with ctx:
        s = get_story(sid)
        assert s["title"] == "Updated"
        assert s["generation_status"] == "pending"
        assert s["tokens_consumed"] == 0
        assert s["is_deleted"] == 0
    assert client.get("/api/v1/stories?page=abc").status_code == 200


def test_negative_token_cost_never_mints_tokens(client, ctx):
    uid = _make_user(ctx, "cost_user")
    with ctx:
        set_setting("token_cost_per_generation", -5, "integer")
        assert generation_cost() == 1
        assert try_deduct(uid, -5, uid) is False
        assert get_user_by_id(uid)["token_balance"] == 5


def test_refill_applies_once_per_interval(client, ctx):
    uid = _make_user(ctx, "refill_user")
    old = (datetime.now(timezone.utc) - timedelta(hours=49)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with ctx:
        db = get_db()
        db.execute("UPDATE tolstoy_users SET last_token_refill_at=? WHERE id=?", (old, uid))
        db.commit()
        assert maybe_refill(uid) == 10
        assert maybe_refill(uid) == 10
        assert get_user_by_id(uid)["token_balance"] == 10


def test_unexpected_generation_error_refunds_and_publishes_next_refill(client, ctx, monkeypatch):
    uid = _make_user(ctx, "gen_user")
    with ctx:
        sid = create_story(uid, "Title", "Content")

    def boom(_story):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(stories_route, "gemini_generate", boom)
    _login(client, uid, "USER")
    r = client.post(f"/api/v1/stories/{sid}/generate")
    assert r.status_code == 502
    with ctx:
        assert get_user_by_id(uid)["token_balance"] == 5
        assert get_story(sid)["generation_status"] == "failed"
    assert r.json["error"]["code"] == "PROVIDER_ERROR"
    assert "unexpected" not in r.json["message"]

    wallet = client.get("/api/v1/wallet").json["data"]
    assert "next_refill_at" in wallet


def test_duplicate_phone_returns_conflict(client, ctx):
    first = {"username": "phone_one", "password": "password123", "phone_number": "+1234567890"}
    assert client.post("/api/v1/auth/register", json=first).status_code == 201
    second = dict(first, username="phone_two")
    assert client.post("/api/v1/auth/register", json=second).status_code == 409


def test_revoked_stories_admin_cannot_edit_other_users_stories(client, ctx):
    admin = _make_user(ctx, "limited_admin", "ADMIN")
    uid = _make_user(ctx, "other_user")
    with ctx:
        sid = create_story(uid, "Title", "Content")
        set_setting("role_permissions", {"USER": [], "ADMIN": ["users_view"], "SUPER_ADMIN": ["*"]}, "json")
    _login(client, admin, "ADMIN")
    assert client.patch(f"/api/v1/stories/{sid}", json={"title": "hacked"}).status_code == 403


def test_last_super_admin_cannot_be_removed(client, ctx):
    uid = _make_user(ctx, "last_super", "SUPER_ADMIN")
    with ctx:
        db = get_db()
        db.execute("UPDATE tolstoy_users SET is_active=0 WHERE role='SUPER_ADMIN' AND id!=?", (uid,))
        db.commit()
        assert update_user(uid, {"role": "USER"}, uid, keep_last_super=True) is False
        assert update_user(uid, {"is_active": 0}, uid, keep_last_super=True) is False
        assert get_user_by_id(uid)["role"] == "SUPER_ADMIN"
        assert get_user_by_id(uid)["is_active"] == 1


def test_gemini_output_shape_is_validated(client, monkeypatch):
    class FakeResponse:
        text = '{"scenes": "not-a-list"}'
        usage_metadata = None

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(gemini_service, "_client", lambda: (FakeClient(), "model"))
    with client.application.app_context():
        with pytest.raises(gemini_service.GeminiError):
            gemini_service.generate({"title": "T", "content": "C"})


def test_production_requires_explicit_secret_key(monkeypatch):
    from app.config import CONFIG_MAP, get_config

    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        get_config("production")
    monkeypatch.setenv("SECRET_KEY", "uniquetestvalue123")
    assert get_config("production") is CONFIG_MAP["production"]


def test_dynamic_tables_escape_stored_text():
    for rel in ("app/templates/admin/stories.html", "app/templates/user/dashboard.html",
                "app/templates/user/stories.html", "app/templates/user/profile.html"):
        assert "esc(" in (ROOT / rel).read_text(encoding="utf-8"), rel
    assert "function esc(" in (ROOT / "app/templates/user/base_user.html").read_text(encoding="utf-8")
