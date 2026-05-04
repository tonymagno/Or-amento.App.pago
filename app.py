from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_DIR = Path("data")
DB_PATH = DB_DIR / "app.db"
PBKDF2_ITERATIONS = 210_000


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1,
                subscription_status TEXT NOT NULL DEFAULT 'inactive',
                plan_expires_at TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                client_name TEXT NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    salt_bytes = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PBKDF2_ITERATIONS,
    )
    return salt_bytes.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, password_hash_hex: str) -> bool:
    salt_bytes = bytes.fromhex(salt_hex)
    _, candidate_hash = _hash_password(password, salt_bytes)
    return hmac.compare_digest(candidate_hash, password_hash_hex)


def create_user(
    username: str,
    password: str,
    role: str = "user",
    is_active: int = 1,
    subscription_status: str = "inactive",
    plan_expires_at: str | None = None,
) -> None:
    init_db()
    salt_hex, password_hash_hex = _hash_password(password)
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO users
            (username, password_salt, password_hash, role, is_active, subscription_status, plan_expires_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                salt_hex,
                password_hash_hex,
                role,
                is_active,
                subscription_status,
                plan_expires_at,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()


def user_count() -> int:
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()
        return int(row["total"]) if row else 0


def get_user(username: str) -> sqlite3.Row | None:
    init_db()
    with _connect() as conn:
        return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def set_subscription(username: str, status: str, expires_at: str | None = None) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE users
            SET subscription_status = ?, plan_expires_at = ?, is_active = 1
            WHERE username = ?
            """,
            (status, expires_at, username),
        )
        conn.commit()


def add_quote(username: str, client_name: str, total: float) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO quotes (username, client_name, total, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, client_name, total, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def recent_quotes(username: str, limit: int = 10) -> list[sqlite3.Row]:
    init_db()
    with _connect() as conn:
        cur = conn.execute(
            """
            SELECT client_name, total, created_at
            FROM quotes
            WHERE username = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (username, limit),
        )
        return cur.fetchall()
