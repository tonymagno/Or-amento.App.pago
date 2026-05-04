# db.py

import sqlite3

DB_PATH = "app.db"

def init_db():
    """
    Inicializa o banco de dados (cria tabelas se não existirem).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabela de usuários (login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        );
    """)
    # Tabela de orçamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            client_name TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def get_user(username):
    """
    Retorna tupla (username, password_hash) do usuário, ou None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_user(username, password_hash):
    """
    Insere um novo usuário no banco (útil para criar o admin).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
                   (username, password_hash))
    conn.commit()
    conn.close()

def add_quote(username, client_name, total):
    """
    Insere um novo orçamento na tabela quotes.
    """
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quotes (username, client_name, total, created_at) VALUES (?, ?, ?, ?)",
        (username, client_name, total, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def recent_quotes(username, limit=5):
    """
    Retorna uma lista dos últimos orçamentos (dicionários) do usuário.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT client_name, total, created_at
        FROM quotes
        WHERE username = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (username, limit))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"client_name": row[0], "total": row[1], "created_at": row[2]}
        for row in rows
    ]
    conn.close()
    return user

def add_user(username, password_hash):
    """Adiciona um novo usuário no DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    conn.close()

def add_quote(username, client_name, total):
    """Adiciona um novo orçamento no DB."""
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quotes (username, client_name, total, created_at)
        VALUES (?, ?, ?, ?)
    """, (username, client_name, total, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def recent_quotes(username, limit=5):
    """Retorna últimos orçamentos de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT client_name, total, created_at 
        FROM quotes 
        WHERE username = ? 
        ORDER BY created_at DESC LIMIT ?
    """, (username, limit))
    rows = cursor.fetchall()
    conn.close()
    # Mapear para dicionários
    return [{"client_name": row[0], "total": row[1], "created_at": row[2]} for row in rows]
