import pytest

from app.models.user import create_user


@pytest.fixture
def ctx(client):
    return client.application.app_context()


def _make_user(ctx, name, role="USER"):
    with ctx:
        return create_user(name, "password123", display_name=name, role=role)


def _login(client, uid, role):
    with client.session_transaction() as s:
        s["user_id"] = uid
        s["role"] = role
        s["username"] = "tester"


def test_public_pages_link_admin_signin(client):
    for path in ("/", "/login"):
        html = client.get(path).get_data(as_text=True)
        assert 'href="/admin/login"' in html, path


def test_dashboard_shows_admin_panel_for_admins_only(client, ctx):
    admin = _make_user(ctx, "nav_super", "SUPER_ADMIN")
    user = _make_user(ctx, "nav_user")

    _login(client, admin, "SUPER_ADMIN")
    html = client.get("/dashboard").get_data(as_text=True)
    assert 'href="/admin"' in html
    assert "Admin Panel" in html

    _login(client, user, "USER")
    html = client.get("/dashboard").get_data(as_text=True)
    assert "Admin Panel" not in html


def test_admin_layout_has_mobile_drawer_controls(client, ctx):
    admin = _make_user(ctx, "drawer_super", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")

    html = client.get("/admin").get_data(as_text=True)
    assert 'data-sidebar-toggle' in html
    assert 'data-sidebar-close' in html
    assert 'data-sidebar-backdrop' in html
