def test_register_and_login(client):
    r = client.post("/api/v1/auth/register", json={"username": "alice", "password": "password123"})
    assert r.status_code == 201
    r = client.post("/api/v1/auth/user/login", json={"username": "alice", "password": "password123"})
    assert r.status_code == 200
    assert r.get_json()["success"] is True


def test_me_requires_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_story_ownership(client):
    client.post("/api/v1/auth/register", json={"username": "alice", "password": "password123"})
    client.post("/api/v1/auth/register", json={"username": "bob", "password": "password123"})
    client.post("/api/v1/auth/user/login", json={"username": "alice", "password": "password123"})
    r = client.post("/api/v1/stories", json={"title": "T", "content": "C"})
    sid = r.get_json()["data"]["story_id"]
    # bob tries to access alice's story
    client.post("/api/v1/auth/logout")
    client.post("/api/v1/auth/user/login", json={"username": "bob", "password": "password123"})
    r = client.get(f"/api/v1/stories/{sid}")
    assert r.status_code == 403


def test_token_initial_balance(client):
    client.post("/api/v1/auth/register", json={"username": "alice", "password": "password123"})
    client.post("/api/v1/auth/user/login", json={"username": "alice", "password": "password123"})
    r = client.get("/api/v1/wallet")
    assert r.get_json()["data"]["token_balance"] == 5


def test_tables_count():
    import sqlite3, os
    # use in-memory via app
    from app import create_app
    app = create_app("testing")
    with app.app_context():
        from app.db import get_db
        tabs = [r[0] for r in get_db().execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tolstoy_%'").fetchall()]
        assert sorted(tabs) == ["tolstoy_stories", "tolstoy_system_settings", "tolstoy_users"]