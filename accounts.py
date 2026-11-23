"""Small SQLite-backed user accounts and personal music library.

Passwords use scrypt with random salts; bearer tokens are stored only as SHA-256 hashes.
For production, add HTTPS, shared ingress throttling, backups, CSRF-safe browser token
handling and account recovery before exposing to untrusted traffic.
"""
import hashlib
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from storage import connect, initialize

def now():
    return datetime.now(timezone.utc)

def init_accounts():
    initialize()
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY, nickname TEXT NOT NULL UNIQUE COLLATE NOCASE,
          password_salt BLOB NOT NULL, password_hash BLOB NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions(
          token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          expires_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS saved_melodies(
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          title TEXT NOT NULL, notation TEXT NOT NULL DEFAULT '',
          source_url TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_melodies_user ON saved_melodies(user_id);
        CREATE TABLE IF NOT EXISTS lesson_progress(
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          lesson_id TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('new','in_progress','completed')),
          updated_at TEXT NOT NULL, PRIMARY KEY(user_id,lesson_id)
        );
        """)

def password_digest(password, salt):
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32)

def register(nickname, password):
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", nickname):
        raise HTTPException(422, "Nickname must be 3-32 ASCII letters, digits or underscores")
    if len(password) < 10 or len(password) > 256:
        raise HTTPException(422, "Password length must be 10-256 characters")
    init_accounts()
    salt = os.urandom(16)
    with connect() as db:
        try:
            cur = db.execute("INSERT INTO users(nickname,password_salt,password_hash,created_at) VALUES(?,?,?,?)",
                             (nickname, salt, password_digest(password, salt), now().isoformat()))
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Nickname already taken")
        return {"id": cur.lastrowid, "nickname": nickname}

def login(nickname, password):
    init_accounts()
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE nickname=? COLLATE NOCASE", (nickname,)).fetchone()
        if row is None:
            # Avoid an easy timing distinction between existing and absent nicknames.
            password_digest(password, b"\x00" * 16)
            raise HTTPException(401, "Invalid credentials")
        if not secrets.compare_digest(password_digest(password, row["password_salt"]), row["password_hash"]):
            raise HTTPException(401, "Invalid credentials")
        token = secrets.token_urlsafe(32)
        db.execute("INSERT INTO sessions(token_hash,user_id,expires_at) VALUES(?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(), row["id"], (now() + timedelta(days=7)).isoformat()))
        return {"access_token": token, "token_type": "bearer", "expires_in": 604800}

def current_user(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer token required")
    token = authorization[7:]
    if len(token) > 256 or not token:
        raise HTTPException(401, "Invalid token")
    init_accounts()
    with connect() as db:
        row = db.execute("""SELECT u.id,u.nickname,s.expires_at FROM sessions s
                            JOIN users u ON u.id=s.user_id WHERE s.token_hash=?""",
                         (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
        if row is None or datetime.fromisoformat(row["expires_at"]) <= now():
            raise HTTPException(401, "Session expired or invalid")
        return {"id": row["id"], "nickname": row["nickname"]}

def logout(token):
    with connect() as db:
        db.execute("DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(token.encode()).hexdigest(),))
