import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "love_data.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            nickname TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            username TEXT NOT NULL,
            nickname TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
            FOREIGN KEY (username) REFERENCES users(username)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            username TEXT NOT NULL,
            nickname TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
            FOREIGN KEY (username) REFERENCES users(username)
        );
    """)
    conn.commit()
    conn.close()
    print("Database initialized!")
