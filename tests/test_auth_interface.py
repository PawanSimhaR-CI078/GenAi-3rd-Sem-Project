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
    assert "right-panel-active" not in login
    assert "right-panel-active" in register
