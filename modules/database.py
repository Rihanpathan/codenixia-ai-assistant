"""
database.py
-----------
SQLite-backed persistence layer.

Tables created on first use:
  • leads        — captured lead records
  • chat_history — chatbot Q&A pairs

Usage:
    from modules.database import init_db, save_lead, get_all_leads, \
                                  save_chat_exchange, get_top_questions

    init_db()          # call once at app startup
"""

import sqlite3
import contextlib
import datetime
from pathlib import Path

import pandas as pd

# ── DB file location (project root / data / leads.db) ────────────────────────
_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "leads.db"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _db_path() -> Path:
    """Return the database file path, creating parent directories if needed."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return _DB_PATH


@contextlib.contextmanager
def _get_conn():
    """Yield a thread-safe SQLite connection with row_factory set."""
    conn = sqlite3.connect(str(_db_path()), check_same_thread=False)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL") # better concurrency
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Initialisation — create tables if they don't exist
# ─────────────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create the `leads` and `chat_history` tables on first run.
    Safe to call repeatedly — uses CREATE TABLE IF NOT EXISTS.
    """
    with _get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                email     TEXT    NOT NULL,
                phone     TEXT,
                interest  TEXT,
                message   TEXT,
                score     INTEGER DEFAULT 0,
                category  TEXT    DEFAULT 'Cold ❄️',
                timestamp TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                question  TEXT NOT NULL,
                response  TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            """
        )
        # Check if category column exists, if not ADD it dynamically
        cursor = conn.execute("PRAGMA table_info(leads)")
        cols = [row[1] for row in cursor.fetchall()]
        if "category" not in cols:
            conn.execute("ALTER TABLE leads ADD COLUMN category TEXT DEFAULT 'Cold ❄️'")


# ─────────────────────────────────────────────────────────────────────────────
# Leads
# ─────────────────────────────────────────────────────────────────────────────

def save_lead(lead_data: dict) -> bool:
    """
    Insert a new lead record.

    Expected keys: name, email, phone, interest, message, score, category.
    A UTC timestamp is added automatically.

    Returns:
        True on success, False on failure.
    """
    required = {"name", "email"}
    if not required.issubset(lead_data):
        raise ValueError(f"lead_data must contain at least: {required}")

    sql = """
        INSERT INTO leads (name, email, phone, interest, message, score, category, timestamp)
        VALUES (:name, :email, :phone, :interest, :message, :score, :category, :timestamp)
    """
    row = {
        "name":      lead_data.get("name", ""),
        "email":     lead_data.get("email", ""),
        "phone":     lead_data.get("phone", ""),
        "interest":  lead_data.get("interest", ""),
        "message":   lead_data.get("message", ""),
        "score":     int(lead_data.get("score", 0)),
        "category":  lead_data.get("category", "Cold ❄️"),
        "timestamp": _now(),
    }

    try:
        with _get_conn() as conn:
            conn.execute(sql, row)
        return True
    except sqlite3.Error as exc:
        print(f"[database] save_lead error: {exc}")
        return False


def get_all_leads() -> pd.DataFrame:
    """
    Retrieve every lead as a pandas DataFrame.

    Columns: id, name, email, phone, interest, message, score, category, timestamp.
    Returns an empty DataFrame (with the correct columns) if no leads exist.
    """
    sql = "SELECT * FROM leads ORDER BY timestamp DESC"
    columns = ["id", "name", "email", "phone", "interest", "message", "score", "category", "timestamp"]

    try:
        with _get_conn() as conn:
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
        if rows:
            return pd.DataFrame([dict(r) for r in rows])
        return pd.DataFrame(columns=columns)
    except sqlite3.Error as exc:
        print(f"[database] get_all_leads error: {exc}")
        return pd.DataFrame(columns=columns)


# ─────────────────────────────────────────────────────────────────────────────
# Chat history
# ─────────────────────────────────────────────────────────────────────────────

def save_chat_exchange(question: str, response: str) -> bool:
    """
    Persist a single chatbot Q&A pair.

    Args:
        question: The user's message.
        response: The assistant's reply.

    Returns:
        True on success, False on failure.
    """
    sql = """
        INSERT INTO chat_history (question, response, timestamp)
        VALUES (?, ?, ?)
    """
    try:
        with _get_conn() as conn:
            conn.execute(sql, (question.strip(), response.strip(), _now()))
        return True
    except sqlite3.Error as exc:
        print(f"[database] save_chat_exchange error: {exc}")
        return False


def get_top_questions(limit: int = 5) -> pd.DataFrame:
    """
    Return the *limit* most-asked questions (exact-match deduplication).

    The query groups identical questions, counts occurrences, and orders
    by frequency descending — so the most commonly asked question is first.

    Returns a DataFrame with columns: question, count.
    """
    sql = """
        SELECT   question,
                 COUNT(*) AS count
        FROM     chat_history
        GROUP BY question
        ORDER BY count DESC
        LIMIT    ?
    """
    try:
        with _get_conn() as conn:
            cursor = conn.execute(sql, (limit,))
            rows = cursor.fetchall()
        if rows:
            return pd.DataFrame([dict(r) for r in rows])
        return pd.DataFrame(columns=["question", "count"])
    except sqlite3.Error as exc:
        print(f"[database] get_top_questions error: {exc}")
        return pd.DataFrame(columns=["question", "count"])


# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
