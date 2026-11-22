import os
import sqlite3
from flask import current_app, g

_MEM_CONN = None


def get_db():
    if "db" in g:
        return g.db
    path = current_app.config["DATABASE_PATH"]
    if path == ":memory:":
        global _MEM_CONN
        if _MEM_CONN is None:
            _MEM_CONN = sqlite3.connect(":memory:", check_same_thread=False)
            _MEM_CONN.row_factory = sqlite3.Row
            _MEM_CONN.execute("PRAGMA foreign_keys = ON")
        conn = _MEM_CONN
    else:
        full = path if os.path.isabs(path) else os.path.join(current_app.root_path, "..", path)
        full = os.path.abspath(full)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        conn = sqlite3.connect(full)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
    g.db = conn
    return g.db


def close_db(e=None):
    path = None
    try:
        path = current_app.config.get("DATABASE_PATH")
    except RuntimeError:
        path = None
    db = g.pop("db", None)
    if db is not None and path != ":memory:":
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(app.root_path, "..", "database", "migrations", "001_initial_schema.sql")
        schema_path = os.path.abspath(schema_path)
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                db.executescript(f.read())
            db.commit()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid