def test_landing_sections_and_copy(client):
    html = client.get("/").get_data(as_text=True)
    for section_id in ("proof", "problem", "how", "features", "tokens", "faq", "start"):
        assert f'id="{section_id}"' in html
    for class_name in ("lp-hero", "lp-script", "lp-proof", "lp-problem", "lp-steps", "lp-benefits", "lp-tokens", "lp-faq", "lp-final"):
        assert class_name in html
    assert '<details name="tolstoy-faq">' in html and "<summary>" in html
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
    assert html.count('<details name="tolstoy-faq">') == 5

    root = Path(__file__).resolve().parents[1]
    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")
    assert "@import url('https://fonts.googleapis.com" not in css
    assert ".lp-script-name, .lp-script-line { font-size: 11px; }" not in css
    assert ".lp-steps .feature-grid::before" in css
    assert "top: calc(var(--space-6) + 19px); left: 16%; right: 16%;" in css
    assert ".lp-faq summary:hover" in css
    assert ".site-footer__col a { color: var(--color-card); font-size: 14px; display: inline-flex; align-items: center; min-height: 40px; }" in css


def test_landing_redesign_tokens_and_readability(client):
    from pathlib import Path

    html = client.get("/").get_data(as_text=True)
    css = (Path(__file__).resolve().parents[1] / "app/static/css/app.css").read_text(encoding="utf-8")

    for token in ("--color-on-primary", "--color-focus", "--color-focus-ring", "--container-max", "--section-space"):
        assert token in css
    assert "font-size: 16px;" in css
    assert "font-size: 18px; line-height: 1.65; color: var(--color-text-secondary);" in css
    assert ":focus-visible { outline: 3px solid var(--color-focus)" in css
    assert "grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-5); }" in css
    for label in ("Account credits", "Refill frequency", "Generation cost"):
        assert label in html
    assert html.count('<svg class="lp-icon"') == 8
    assert html.count('aria-hidden="true"') >= 8
    assert 'aria-labelledby="faq-heading"' in html


def test_landing_responsive_and_type_fixes(client):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    html = client.get("/").get_data(as_text=True)
    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")
    js = (root / "app/static/js/app.js").read_text(encoding="utf-8")

    assert 'name="description" content="TOLSTOY turns your story idea' in html
    assert 'aria-labelledby="proof-heading"' in html
    assert '<h2 id="proof-heading" class="lp-eyebrow">The short version</h2>' in html
    assert '<h3>5 tokens when you sign up, plus 5 every 48 hours</h3>' in html

    assert "@media (max-width: 900px)" in css
    assert ".lp-proof-grid, .lp-benefits .feature-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }" in css
    assert "@media (min-width: 901px)" in css
    assert "font-size: 14px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--color-primary);" in css
    assert ".lp-problem .lp-eyebrow, .lp-steps .lp-eyebrow, .lp-benefits .lp-eyebrow, .lp-tokens-wrap .lp-eyebrow" in css
    assert ".lp-hero .badge { padding: 6px 10px; font-size: 13px; }" in css
    assert "font-family: var(--font-mono); font-size: 14px; line-height: 1.5;" in css
    assert "font-family: var(--font-mono); font-size: 13px; font-weight: 600; letter-spacing: .08em;" in css
    assert "window.innerWidth > 900" in js
