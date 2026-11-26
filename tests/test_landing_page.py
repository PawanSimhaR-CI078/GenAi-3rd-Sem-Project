def test_landing_sections_and_copy(client):
    html = client.get("/").get_data(as_text=True)
    for section_id in ("proof", "problem", "how", "features", "tokens", "faq", "start"):
        assert f'id="{section_id}"' in html
    for class_name in ("lp-hero", "lp-script", "lp-proof", "lp-problem", "lp-steps", "lp-benefits", "lp-tokens", "lp-faq", "lp-final"):
        assert class_name in html
    assert "<details>" in html and "<summary>" in html
    assert "5 tokens" in html and "48 hours" in html
    assert "no images" in html.lower()
    assert "<img" not in html.lower()


def test_public_nav_and_shared_footer(client):
    html = client.get("/").get_data(as_text=True)
    assert 'class="public-nav public-nav--landing"' in html
    assert 'href="/#how"' in html and 'href="/#faq"' in html
    for heading in ("Product", "Resources", "Company", "Legal"):
        assert heading in html
    assert 'href="/maintenance"' in html
    for path in ("/login", "/register", "/admin/login", "/maintenance"):
        page = client.get(path).get_data(as_text=True)
        assert "site-footer__grid" in page, path


def test_landing_styles(client):
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "app/static/css/app.css").read_text(encoding="utf-8")
    for selector in (".lp-hero", ".lp-script", ".lp-proof", ".lp-steps", ".lp-benefits", ".lp-tokens", ".lp-faq", ".lp-final", ".site-footer__grid"):
        assert selector in css
    assert ".lp-final :focus-visible" in css
    assert ".site-footer :focus-visible" in css
    assert "@media (max-width: 768px)" in css
    assert "prefers-reduced-motion" in css
    assert "html { scroll-behavior: auto; }" in css


def test_landing_has_accessible_mobile_navigation(client):
    from pathlib import Path

    html = client.get("/").get_data(as_text=True)
    assert 'data-nav-toggle' in html
    assert 'aria-controls="publicNav"' in html
    assert 'id="publicNav"' in html
    assert 'aria-expanded="false"' in html
    assert 'aria-label="Open navigation"' not in html

    root = Path(__file__).resolve().parents[1]
    js = (root / "app/static/js/app.js").read_text(encoding="utf-8")
    assert "data-nav-toggle" in js
    assert "aria-expanded" in js
    assert "Escape" in js
    assert "toggle.focus()" in js
    assert "pointerdown" in js
    assert "toggle.setAttribute('aria-label'" not in js

    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")
    assert ".nav-toggle" in css
    assert ".public-nav--landing nav.is-open" in css


def test_landing_refinements(client):
    from pathlib import Path

    html = client.get("/").get_data(as_text=True)
    assert 'class="btn btn-primary">Create an account</a>' in html
    assert 'id="tokens"' in html and 'id="faq"' in html
    assert html.count("<details>") == 5

    root = Path(__file__).resolve().parents[1]
    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")
    assert "@import url('https://fonts.googleapis.com" not in css
    assert ".lp-script-name, .lp-script-line { font-size: 11px; }" not in css
    assert ".lp-steps .feature-grid::before" in css
    assert "top: calc(var(--space-5) + 12px); left: 16%; right: 16%;" in css
    assert ".lp-faq summary:hover" in css
    assert ".site-footer__col a { color: var(--color-card); font-size: 13px; display: inline-flex; align-items: center; min-height: 24px; }" in css
