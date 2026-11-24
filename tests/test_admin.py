import pytest
from app import create_app
from app.models.user import create_user, get_user_by_id
from app.models.system_settings import set_setting
from app.security import DEFAULT_ROLE_PERMISSIONS, SUPER_ONLY_CAPABILITIES
from app.schemas.validators import validate_username
from app.services.bootstrap import bootstrap


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


def _json(response):
    return response.get_json()


def test_default_permissions_lock_super_capabilities():
    admin = set(DEFAULT_ROLE_PERMISSIONS["ADMIN"])
    assert not (admin & SUPER_ONLY_CAPABILITIES)
    assert {"analytics", "users_view", "users_edit", "database", "stories_admin"} <= admin
    assert "settings" not in admin
    assert "system" not in admin
    assert "roles_view" not in admin
    assert "wallet_edit" not in admin


def test_username_allows_single_spaces():
    assert validate_username("Pawan Simha R")
    assert validate_username("Ramesh")
    assert not validate_username(" leading")
    assert not validate_username("double  space")


def test_token_increase_only(client, ctx):
    admin = _make_user(ctx, "root_admin", "SUPER_ADMIN")
    uid = _make_user(ctx, "token_user")
    _login(client, admin, "SUPER_ADMIN")

    r = client.patch(f"/api/v1/admin/users/{uid}/tokens", json={"increase": 5})
    assert r.status_code == 200
    with ctx:
        assert get_user_by_id(uid)["token_balance"] == 10

    for body in ({"token_balance": 1}, {"adjustment": -3}, {"increase": -2}, {"increase": 0}):
        r = client.patch(f"/api/v1/admin/users/{uid}/tokens", json=body)
        assert r.status_code == 400, body
    with ctx:
        assert get_user_by_id(uid)["token_balance"] == 10


def test_admin_cannot_edit_wallet(client, ctx):
    admin = _make_user(ctx, "wallet_admin", "ADMIN")
    uid = _make_user(ctx, "wallet_user")
    _login(client, admin, "ADMIN")

    assert client.patch(f"/api/v1/admin/users/{uid}/tokens", json={"increase": 5}).status_code == 403
    with ctx:
        assert get_user_by_id(uid)["token_balance"] == 5


def test_admin_blocked_from_super_only_pages_and_apis(client, ctx):
    admin = _make_user(ctx, "limited_admin", "ADMIN")
    _login(client, admin, "ADMIN")

    for path in ("/admin/roles", "/admin/system", "/admin/settings"):
        assert client.get(path).status_code == 403, path
    for path in ("/api/v1/admin/roles/permissions", "/api/v1/admin/system/status"):
        assert client.get(path).status_code == 403, path
    assert client.patch("/api/v1/admin/maintenance", json={"enabled": True, "password": "password123"}).status_code == 403
    assert client.get("/api/v1/admin/settings").status_code == 403


def test_admin_allowed_pages_and_profile_edit(client, ctx):
    admin = _make_user(ctx, "normal_admin", "ADMIN")
    uid = _make_user(ctx, "profile_user")
    _login(client, admin, "ADMIN")

    for path in ("/admin", "/admin/users", "/admin/database", "/admin/stories"):
        assert client.get(path).status_code == 200, path
    assert client.get("/api/v1/admin/analytics/summary").status_code == 200
    assert client.get("/api/v1/admin/database/tolstoy_users").status_code == 200
    r = client.patch(f"/api/v1/admin/users/{uid}", json={"display_name": "Renamed"})
    assert r.status_code == 200
    with ctx:
        assert get_user_by_id(uid)["display_name"] == "Renamed"


def test_super_admin_has_every_page(client, ctx):
    admin = _make_user(ctx, "all_super", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")
    for path in ("/admin", "/admin/users", "/admin/roles", "/admin/database",
                 "/admin/stories", "/admin/settings", "/admin/system"):
        r = client.get(path)
        assert r.status_code == 200, (path, r.status_code)


def test_user_edit_validation_and_role_guard(client, ctx):
    admin = _make_user(ctx, "role_admin", "SUPER_ADMIN")
    uid = _make_user(ctx, "edit_user")
    _make_user(ctx, "other_user")
    _login(client, admin, "SUPER_ADMIN")

    assert client.patch(f"/api/v1/admin/users/{uid}", json={"username": "other_user"}).status_code == 409
    assert client.patch(f"/api/v1/admin/users/{uid}", json={"display_name": "New Name"}).status_code == 200

    assert client.patch(f"/api/v1/admin/users/{uid}/role", json={"role": "ADMIN", "password": "wrong"}).status_code == 401
    assert client.patch(f"/api/v1/admin/users/{uid}/role", json={"role": "ADMIN", "password": "password123"}).status_code == 200
    with ctx:
        assert get_user_by_id(uid)["role"] == "ADMIN"


def test_permissions_enforced(client, ctx):
    super_id = _make_user(ctx, "perm_super", "SUPER_ADMIN")
    admin_id = _make_user(ctx, "perm_admin", "ADMIN")
    with ctx:
        set_setting("role_permissions", {"USER": [], "ADMIN": [], "SUPER_ADMIN": ["*"]}, "json")

    _login(client, admin_id, "ADMIN")
    assert client.get("/api/v1/admin/users").status_code == 403

    _login(client, super_id, "SUPER_ADMIN")
    assert client.get("/api/v1/admin/users").status_code == 200
    assert client.put("/api/v1/admin/roles/permissions", json={"permissions": {
        "USER": [], "ADMIN": ["users_view", "wallet_edit"], "SUPER_ADMIN": ["*"]}}).status_code == 403
    assert client.put("/api/v1/admin/roles/permissions", json={"permissions": {
        "USER": [], "ADMIN": ["users_view"], "SUPER_ADMIN": ["*"]}}).status_code == 200

    _login(client, admin_id, "ADMIN")
    assert client.get("/api/v1/admin/users").status_code == 200
    assert client.patch("/api/v1/admin/users/2/tokens", json={"increase": 1}).status_code == 403


def test_locked_matrix_entries_are_stripped(client, ctx):
    super_id = _make_user(ctx, "strip_super", "SUPER_ADMIN")
    admin_id = _make_user(ctx, "strip_admin", "ADMIN")
    with ctx:
        set_setting("role_permissions", {
            "USER": [],
            "ADMIN": ["users_view", "system", "roles_view", "settings", "wallet_edit"],
            "SUPER_ADMIN": ["*"],
        }, "json")

    _login(client, admin_id, "ADMIN")
    assert client.get("/admin/system").status_code == 403
    assert client.get("/api/v1/admin/system/status").status_code == 403
    assert client.patch("/api/v1/admin/maintenance", json={"enabled": True, "password": "password123"}).status_code == 403

    _login(client, super_id, "SUPER_ADMIN")
    assert client.get("/api/v1/admin/roles/permissions").json["data"]["locked"]


def test_maintenance_blocks_users_not_admins_and_survives_bootstrap(client, ctx):
    admin = _make_user(ctx, "maint_admin", "SUPER_ADMIN")
    uid = _make_user(ctx, "maint_user")
    _login(client, admin, "SUPER_ADMIN")

    r = client.patch("/api/v1/admin/maintenance", json={"enabled": True, "password": "wrong"})
    assert r.status_code == 401
    r = client.patch("/api/v1/admin/maintenance", json={"enabled": True, "password": "password123"})
    assert r.status_code == 200

    _login(client, uid, "USER")
    assert client.get("/api/v1/stories").status_code == 503
    assert client.get("/dashboard").status_code == 302

    _login(client, admin, "SUPER_ADMIN")
    assert client.get("/admin").status_code == 200
    with ctx:
        bootstrap()
    assert _json(client.get("/api/v1/admin/system/status"))["data"]["enabled"] is True


def test_database_viewer_safety(client, ctx):
    admin = _make_user(ctx, "db_admin", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")

    assert client.get("/api/v1/admin/database/not_a_table").status_code == 400
    r = client.get("/api/v1/admin/database/tolstoy_users")
    assert r.status_code == 200
    body = _json(r)["data"]
    assert "password_hash" not in body["columns"]
    assert all("password_hash" not in row for row in body["rows"])
    assert body["total"] >= 1

    r = client.get("/api/v1/admin/database/meta")
    assert set(r.json["data"]["counts"]) == {"tolstoy_users", "tolstoy_stories", "tolstoy_system_settings"}


def test_analytics_and_integrity(client, ctx):
    admin = _make_user(ctx, "analytics_admin", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")

    s = _json(client.get("/api/v1/admin/analytics/summary?range=7"))
    assert s["success"] and set(s["data"]) == {"users", "stories", "tokens", "system"}
    c = _json(client.get("/api/v1/admin/analytics/charts?chart=stories_status"))
    assert c["data"]["labels"] == ["Editing", "Completed"]
    h = _json(client.get("/api/v1/admin/analytics/db-health"))
    assert h["data"]["size_bytes"] > 0
    i = _json(client.get("/api/v1/admin/analytics/integrity"))
    assert i["data"]["integrity"] == "ok"


def test_role_change_cannot_demote_last_super_admin(client, ctx):
    admin = _make_user(ctx, "last_super", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")
    r = client.patch(f"/api/v1/admin/users/{admin}/role", json={"role": "USER", "password": "password123"})
    assert r.status_code == 403
