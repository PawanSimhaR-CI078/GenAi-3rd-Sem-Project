from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _html():
    return (ROOT / "app/templates/admin/roles.html").read_text(encoding="utf-8")


def _css():
    return (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")


def test_editable_cells_are_accessible_switches():
    html = _html()
    assert 'class="perm-switch" type="checkbox" role="switch"' in html
    assert 'aria-label="${esc(label)} for ${r}"' in html
    assert 'data-cap="${key}" data-role="${r}"' in html
    assert "${editable?'':'disabled'}" in html


def test_locked_and_full_cells_stay_text():
    html = _html()
    assert "✓ Full" in html
    assert "lock" in html
    assert "perm-switch" not in html.split("if(r==='SUPER_ADMIN')")[1].split("if(locked.includes(key))")[0]
    assert "perm-switch" not in html.split("if(locked.includes(key))")[1].split("const checked=")[0]


def test_save_payload_is_unchanged():
    html = _html()
    assert "document.querySelectorAll('#matrixBody input[type=checkbox]')" in html
    assert "el.checked" in html
    assert "out[el.dataset.role].push(el.dataset.cap)" in html
    assert "out={USER:[],ADMIN:[],SUPER_ADMIN:['*']}" in html


def test_switch_styles_use_brand_tokens_and_respect_reduced_motion():
    css = _css()
    block = css.split("/* Role access switches */")[-1]
    assert ".perm-switch" in block
    assert "appearance: none" in block
    assert "var(--color-primary)" in block
    assert "var(--color-border)" in block
    assert ":focus-visible" in block
    assert "@media (prefers-reduced-motion: reduce)" in block
    assert ".perm-switch { transition: none; }" in block
    for color in ("FF4B2B", "FF416C", "Montserrat", "fa-"):
        assert color not in block
