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
