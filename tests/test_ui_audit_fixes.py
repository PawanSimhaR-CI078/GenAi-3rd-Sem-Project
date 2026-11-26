"""Regression checks for the UI/UX audit fixes."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")


def _hex(token):
    match = re.search(rf"--color-{token}:\s*(#[0-9A-Fa-f]{{6}})", CSS)
    assert match, token
    return match.group(1).lstrip("#")


def _luminance(value):
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def test_muted_text_meets_aa_contrast():
    for foreground in ("text-muted", "text-secondary"):
        text = _luminance(_hex(foreground))
        for token in ("bg", "card", "bg-secondary"):
            base = _luminance(_hex(token))
            ratio = (max(text, base) + 0.05) / (min(text, base) + 0.05)
            assert ratio >= 4.5, (foreground, token, ratio)


def test_feature_grids_match_card_counts():
    assert ".lp-steps .feature-grid { grid-template-columns: repeat(3, minmax(0, 1fr));" in CSS
    assert ".lp-benefits .feature-grid { grid-template-columns: repeat(4, minmax(0, 1fr));" in CSS


def test_toasts_are_screen_reader_announced():
    for relative in ("user/base_user.html", "admin/base_admin.html"):
        html = (ROOT / "app/templates" / relative).read_text(encoding="utf-8")
        assert 'id="toasts" role="status" aria-live="polite"' in html


def test_authenticated_layouts_have_main_landmark():
    for relative in ("user/base_user.html", "admin/base_admin.html"):
        html = (ROOT / "app/templates" / relative).read_text(encoding="utf-8")
        assert '<main class="main-content">' in html


def test_pages_declare_a_favicon_to_avoid_404():
    for relative in ("public/base_public.html", "user/base_user.html", "admin/base_admin.html"):
        html = (ROOT / "app/templates" / relative).read_text(encoding="utf-8")
        assert '<link rel="icon" href="data:,">' in html


def test_password_toggles_have_accessible_names():
    shell = (ROOT / "app/templates/public/_auth_shell.html").read_text(encoding="utf-8")
    script = (ROOT / "app/templates/public/_auth_script.html").read_text(encoding="utf-8")
    assert 'aria-label="Show sign-in password"' in shell
    assert 'aria-label="Show registration password"' in shell
    assert "setAttribute('aria-label'" in script
