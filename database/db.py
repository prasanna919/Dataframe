"""
SQLite helper for persisting CSV cleaning session history.
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "sessions.db")

def init_db():
    """Creates the sessions table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT NOT NULL,
            rows_before INTEGER,
            rows_after  INTEGER,
            cols_before INTEGER,
            cols_after  INTEGER,
            duplicates_removed INTEGER,
            operations  TEXT,
            logs        TEXT,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_session(filename, summary, operations, logs):
    """
    Persists a cleaning session to the database.
    
    Args:
        filename (str): Original file name.
        summary (dict): Keys: rows_before, rows_after, cols_before, cols_after,
                        duplicates_before, duplicates_after.
        operations (list): List of operation dicts that were applied.
        logs (list): Human-readable log strings.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions
            (filename, rows_before, rows_after, cols_before, cols_after,
             duplicates_removed, operations, logs, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        summary.get("rows_before"),
        summary.get("rows_after"),
        summary.get("columns_before"),
        summary.get("columns_after"),
        summary.get("duplicates_before", 0) - summary.get("duplicates_after", 0),
        json.dumps(operations),
        json.dumps(logs),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def get_sessions(limit=20):
    """
    Retrieves recent cleaning sessions, newest first.
    
    Returns:
        list of dicts with session fields.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "filename": row["filename"],
            "rows_before": row["rows_before"],
            "rows_after": row["rows_after"],
            "cols_before": row["cols_before"],
            "cols_after": row["cols_after"],
            "duplicates_removed": row["duplicates_removed"],
            "operations": json.loads(row["operations"]) if row["operations"] else [],
            "logs": json.loads(row["logs"]) if row["logs"] else [],
            "created_at": row["created_at"]
        })
    return result
