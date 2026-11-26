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


def test_sidebar_icons_sized_and_admin_active_scoped(client, ctx):
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "app/static/css/app.css").read_text(encoding="utf-8")
    assert ".nav-icon { width: 20px; height: 20px; flex: 0 0 20px; }" in css
    assert ".sidebar-admin .nav-link.active" in css
    assert ".sidebar-admin .nav-link:not(.active) { color: #B9C1D4; }" in css

    admin = _make_user(ctx, "sidebar_super", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")
    assert 'class="sidebar sidebar-admin"' in client.get("/admin").get_data(as_text=True)


def test_admin_sidebar_icons_are_valid_material_ligatures():
    import re
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "app/templates/admin/base_admin.html").read_text(encoding="utf-8")
    icons = re.findall(r'<i class="material-icons">([^<]+)</i>', html)
    assert icons
    assert set(icons) <= {
        "dashboard", "home", "people", "security", "storage", "auto_stories",
        "how_to_reg", "settings", "system_update",
    }


def test_super_admin_sidebar_lists_all_eight_admin_pages(client, ctx):
    admin = _make_user(ctx, "nav_all_super", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")

    html = client.get("/admin").get_data(as_text=True)
    for path in ("/admin", "/admin/users", "/admin/roles", "/admin/assign-roles",
                 "/admin/database", "/admin/stories", "/admin/settings", "/admin/system"):
        assert f'href="{path}"' in html, path


def test_admin_sidebar_hides_assign_roles(client, ctx):
    admin = _make_user(ctx, "nav_admin_limited", "ADMIN")
    _login(client, admin, "ADMIN")

    html = client.get("/admin").get_data(as_text=True)
    assert 'href="/admin/assign-roles"' not in html
    assert 'href="/admin/settings"' not in html


def test_sidebars_collapse_to_google_icon_rail(client, ctx):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    admin = (root / "app/templates/admin/base_admin.html").read_text(encoding="utf-8")
    user = (root / "app/templates/user/base_user.html").read_text(encoding="utf-8")
    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")
    for html in (admin, user):
        assert 'data-sidebar-collapse' in html
        assert 'class="nav-label"' in html
        assert "sessionStorage.getItem('tolstoy_sidebar_collapsed') === '1'" in html
    assert '<svg' not in user
    assert '<link href="https://fonts.googleapis.com/icon?family=Material+Icons"' in user
    assert '.sidebar-collapsed .sidebar { width: var(--sidebar-collapsed-width);' in css
    assert '.main-content { flex: 1; padding: var(--space-6); min-width: 0; height: 100vh; overflow-y: auto;' in css
    assert 'position: sticky' not in css


def test_assign_roles_page_has_search_input(client, ctx):
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "app/templates/admin/assign_roles.html").read_text(encoding="utf-8")
    assert 'id="search"' in html
    assert 'id="search" class="form-input mb-3" style="max-width:260px;" placeholder="Search users" autocomplete="off"' in html
    assert 'type="password" class="form-input" placeholder="••••••••" autocomplete="new-password"' in html


def test_role_access_has_no_embedded_assignment(client, ctx):
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "app/templates/admin/roles.html").read_text(encoding="utf-8")
    assert 'id="tbody"' not in html
    assert ">Assign roles<" not in html


def test_welcome_page_requires_login(client):
    r = client.get("/home")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_welcome_page_links_dashboards_by_role(client, ctx):
    admin = _make_user(ctx, "welcome_super", "SUPER_ADMIN")
    user = _make_user(ctx, "welcome_user")

    _login(client, user, "USER")
    html = client.get("/home").get_data(as_text=True)
    assert 'href="/dashboard"' in html
    assert 'href="/stories/new"' in html
    assert 'href="/admin"' not in html

    _login(client, admin, "SUPER_ADMIN")
    html = client.get("/admin/home").get_data(as_text=True)
    assert 'href="/admin"' in html
    assert 'href="/admin/users"' in html
    assert 'data-auth="1"' in html


def test_admin_home_redirects_from_shared_home(client, ctx):
    admin = _make_user(ctx, "welcome_redirect_super", "SUPER_ADMIN")
    _login(client, admin, "SUPER_ADMIN")
    r = client.get("/home")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/admin/home")


def test_welcome_page_is_auth_scoped(client, ctx):
    user = _make_user(ctx, "welcome_tab_user")
    _login(client, user, "USER")
    assert 'data-auth="1"' in client.get("/home").get_data(as_text=True)


def test_welcome_page_survives_maintenance_for_admin(client, ctx):
    from app.models.system_settings import set_setting

    admin = _make_user(ctx, "welcome_maint_super", "SUPER_ADMIN")
    user = _make_user(ctx, "welcome_maint_user")
    with ctx:
        set_setting("maintenance_mode", True, "boolean")
    try:
        _login(client, admin, "SUPER_ADMIN")
        assert client.get("/home", follow_redirects=True).status_code == 200
        _login(client, user, "USER")
        r = client.get("/home")
        assert r.status_code == 302
        assert "/maintenance" in r.headers["Location"]
    finally:
        with ctx:
            set_setting("maintenance_mode", False, "boolean")


def test_login_forms_redirect_to_welcome_page():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    login = (root / "app/templates/public/login.html").read_text(encoding="utf-8")
    admin_login = (root / "app/templates/public/admin_login.html").read_text(encoding="utf-8")
    for html in (login, admin_login):
        assert "sessionStorage.setItem('tolstoy_tab','1')" in html
        assert "'/admin/home'" in html
    assert "'/home'" in login
    assert "'/dashboard'" not in login
    assert "window.location='/admin/home'" in admin_login


def test_welcome_page_has_workspace_tiles(client, ctx):
    user = _make_user(ctx, "welcome_tiles_user")
    _login(client, user, "USER")
    html = client.get("/home").get_data(as_text=True)
    for tile_id in ("wsVal1", "wsVal2", "wsVal3", "wsVal4", "wsRecent", "workspace"):
        assert f'id="{tile_id}"' in html
    assert "aria-busy=\"true\"" in html


def test_welcome_link_in_both_sidebars(client, ctx):
    user = _make_user(ctx, "welcome_nav_user")
    admin = _make_user(ctx, "welcome_nav_super", "SUPER_ADMIN")

    _login(client, user, "USER")
    html = client.get("/home").get_data(as_text=True)
    assert 'href="/home"' in html
    assert '>home</i>' in html
    assert "Welcome</span>" in html

    _login(client, admin, "SUPER_ADMIN")
    html = client.get("/admin/home").get_data(as_text=True)
    assert 'href="/admin/home"' in html
    assert '>home</i>' in html
    assert "Welcome</span>" in html


def test_analytics_kpi_tones_and_marque_polish(client, ctx):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    html = (root / "app/templates/admin/dashboard.html").read_text(encoding="utf-8")
    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")

    assert "card('Generation success'" in html
    assert "'good'" in html
    assert "'bad'" in html
    assert "kpi-tone--" in html
    assert ".kpi-grid > .stat-card.kpi-tone--good" in css
    assert ".kpi-grid > .stat-card.kpi-tone--bad" in css
    assert "repeating-linear-gradient" in css
    assert "translateY(-3px)" in css


def test_gemini_mark_and_rounded_bar_tops(client, ctx):
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "app/templates/admin/dashboard.html").read_text(encoding="utf-8")
    assert "GEMINI_MARK" in html
    assert 'aria-hidden="true"' in html
    assert "Gemini tokens" in html
    assert "borderRadius: 8" in html
    assert "borderSkipped: 'bottom'" in html
