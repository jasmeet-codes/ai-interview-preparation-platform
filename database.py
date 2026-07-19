"""
database.py
------------
Thin wrapper around Python's built-in sqlite3 module. No ORM is used so the
schema stays transparent and easy to inspect/extend.

Tables:
    users        - login credentials + profile
    interviews   - one row per interview session (category/difficulty/role)
    qa_records   - one row per question asked inside an interview, with the
                   user's answer, AI score (1-10), feedback, strengths,
                   weaknesses, suggestions
    resumes      - uploaded resume metadata + AI analysis text
"""

import sqlite3
import os
from flask import g, current_app


def get_db():
    """Return a SQLite connection stored on Flask's application context `g`,
    so the same connection is reused for the duration of one request."""
    if "db" not in g:
        os.makedirs(os.path.dirname(current_app.config["DATABASE_PATH"]), exist_ok=True)
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row  # lets us access columns by name
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the DB connection at the end of the request (registered in app.py)."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    target_role     TEXT DEFAULT 'Software Engineer',
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS interviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category        TEXT NOT NULL,
    difficulty      TEXT NOT NULL,
    role            TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'in_progress', -- in_progress | completed
    avg_score       REAL DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now')),
    completed_at    TEXT
);

CREATE TABLE IF NOT EXISTS qa_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    interview_id    INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_text   TEXT NOT NULL,
    answer_text     TEXT,
    score           INTEGER,             -- 1-10
    feedback        TEXT,
    strengths       TEXT,
    weaknesses      TEXT,
    suggestions     TEXT,
    answered_at     TEXT
);

CREATE TABLE IF NOT EXISTS resumes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    analysis        TEXT,               -- JSON string: score, strengths, gaps, tips
    uploaded_at     TEXT DEFAULT (datetime('now'))
);
"""


def init_db(app):
    """Create tables if they don't already exist. Safe to call every startup."""
    os.makedirs(os.path.dirname(app.config["DATABASE_PATH"]), exist_ok=True)
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
