import time

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
        s["username"] = "session_user"


def test_idle_session_logs_out(client, ctx):
    _login(client, _make_user(ctx, "idle_user"), "USER")
    with client.session_transaction() as s:
        s["last_activity"] = int(time.time()) - 2701

    assert client.get("/dashboard").status_code == 302
    assert client.get("/api/v1/auth/me").status_code == 401


def test_activity_refreshes_idle_timer(client, ctx):
    _login(client, _make_user(ctx, "active_user"), "USER")
    with client.session_transaction() as s:
        s["last_activity"] = int(time.time()) - 2600

    assert client.get("/dashboard").status_code == 200
    with client.session_transaction() as s:
        assert s["last_activity"] >= int(time.time()) - 60


def test_admin_page_marks_tab_scope(client, ctx):
    _login(client, _make_user(ctx, "tab_super", "SUPER_ADMIN"), "SUPER_ADMIN")

    assert 'data-auth="1"' in client.get("/admin").get_data(as_text=True)


def test_analytics_charts_have_bounded_container(client, ctx):
    _login(client, _make_user(ctx, "chart_super", "SUPER_ADMIN"), "SUPER_ADMIN")

    html = client.get("/admin").get_data(as_text=True)
    assert html.count('class="chart-box"') == 9
