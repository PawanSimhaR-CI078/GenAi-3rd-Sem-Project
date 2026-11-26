def test_login_and_register_share_auth_shell(client):
    login = client.get("/login").get_data(as_text=True)
    register = client.get("/register").get_data(as_text=True)
    for html in (login, register):
        assert "auth-wrapper--split" in html
        assert "auth-form-panel--signin" in html
        assert "auth-form-panel--signup" in html
        assert "auth-overlay-container" in html
        assert "auth-mode-switch" in html
        for required in ("loginForm", "registerForm", "loginMsg", "registerMsg",
                         "loginUsername", "loginPassword", "registerUsername",
                         "registerDisplayName", "registerPassword"):
            assert required in html
        assert 'role="alert"' in html
        assert 'href="#"' not in html
        assert "fa-" not in html
        assert "Montserrat" not in html
        assert "FF4B2B" not in html and "FF416C" not in html

    assert 'data-auth-mode="login"' in login
    assert 'data-auth-mode="register"' in register
    assert 'id="authContainer" class="auth-shell"' in login
    assert 'id="authContainer" class="auth-shell right-panel-active"' in register


def test_auth_shell_exposes_controls_and_live_regions(client):
    for path in ("/login", "/register"):
        html = client.get(path).get_data(as_text=True)
        for control_id in ("authSignInBtn", "authSignUpBtn", "loginSubmitBtn",
                           "registerSubmitBtn", "authMobileSignIn", "authMobileSignUp"):
            assert f'id="{control_id}"' in html, (path, control_id)
        assert html.count('aria-live="polite"') == 2, path
        assert html.count("data-pw-toggle=") == 2, path


def test_shared_auth_script_uses_real_endpoints(client):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    script = (root / "app/templates/public/_auth_script.html").read_text(encoding="utf-8")
    html = client.get("/login").get_data(as_text=True)

    assert "history.replaceState" in script
    assert "'/login'" in script and "'/register'" in script
    assert "/api/v1/auth/user/login" in script
    assert "/api/v1/auth/register" in script
    assert "sessionStorage.setItem('tolstoy_tab','1')" in script
    assert "'/admin/home'" in script and "'/home'" in script
    assert ".focus()" in script
    assert "authReady" in script
    assert "_auth_script.html" not in html
    assert "loginForm" in html


def test_shared_auth_script_only_hides_panels_on_mobile():
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    script = (root / "app/templates/public/_auth_script.html").read_text(encoding="utf-8")

    assert "window.matchMedia('(max-width: 768px)')" in script
    assert "mobileQuery.addEventListener('change'" in script
    branches = re.search(r"if \(mobileQuery\.matches\) \{(.*?)\} else \{(.*?)\}", script, re.S)
    assert branches
    assert "signInPanel.hidden = register;" in branches.group(1)
    assert "signUpPanel.hidden = !register;" in branches.group(1)
    assert "signInPanel.hidden = false;" in branches.group(2)
    assert "signUpPanel.hidden = false;" in branches.group(2)


def test_auth_interface_styles(client):
    from pathlib import Path

    css = (Path(__file__).resolve().parents[1] / "app/static/css/app.css").read_text(encoding="utf-8")
    for selector in (".auth-wrapper--split", ".auth-shell", ".auth-form-panel",
                     ".auth-overlay-container", ".auth-overlay-panel", ".auth-mode-switch",
                     ".auth-error", ".right-panel-active"):
        assert selector in css
    assert "#5546E8" not in css.split("/* Auth interface */")[-1].replace("--color-primary: #5546E8;", "")
    assert "FF4B2B" not in css and "FF416C" not in css
    assert "@media (max-width: 768px)" in css.split("/* Auth interface */")[-1]
    assert "@media (prefers-reduced-motion: reduce)" in css.split("/* Auth interface */")[-1]
    assert ".auth-shell :focus-visible" in css


def test_auth_css_keeps_hidden_panels_and_focus_states():
    import re
    from pathlib import Path

    css = (Path(__file__).resolve().parents[1] / "app/static/css/app.css").read_text(encoding="utf-8")
    hidden_rule = ".auth-form-panel[hidden] { display: none; }"
    assert hidden_rule in css
    assert not re.search(r"\.auth-form-panel\s*\{[^}]*\bdisplay\s*:", css.split(hidden_rule, 1)[1])

    desktop = css.split("@media (min-width: 769px) {", 1)[1].split("\n}", 1)[0]
    for rule in (".auth-form-panel--signup { visibility: hidden; }",
                 ".auth-form-panel--signin { visibility: visible; }",
                 ".auth-shell.right-panel-active .auth-form-panel--signup { visibility: visible; }",
                 ".auth-shell.right-panel-active .auth-form-panel--signin { visibility: hidden; }"):
        assert rule in desktop

    focus_rule = ".auth-shell :focus-visible { outline-color: var(--color-primary-hover); outline-offset: 3px; }"
    overlay_focus_rule = ".auth-overlay-panel :focus-visible { outline-color: var(--color-card); }"
    assert overlay_focus_rule in css
    assert css.index(overlay_focus_rule) > css.index(focus_rule)
