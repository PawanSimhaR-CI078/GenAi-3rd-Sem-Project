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
