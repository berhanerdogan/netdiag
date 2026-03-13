import sqlite3
from datetime import datetime


class Database:
    """All persistence lives here. One instance shared by every page."""

    def __init__(self, path="netdiag.db"):
        self._path = path
        self._setup()

    def _connect(self):
        return sqlite3.connect(self._path)

    def _setup(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT    NOT NULL,
                    command   TEXT    NOT NULL,
                    target    TEXT    NOT NULL,
                    result    TEXT,
                    status    TEXT    NOT NULL
                )
            """)
            conn.commit()

    def insert(self, command, target, result, status):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO logs (timestamp, command, target, result, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (ts, command, target, result, status)
            )
            conn.commit()

    def all(self):
        """Return all rows, newest first."""
        with self._connect() as conn:
            return conn.execute(
                "SELECT id, timestamp, command, target, result, status "
                "FROM logs ORDER BY id DESC"
            ).fetchall()

    def count(self):
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]

    def count_by_command(self):
        with self._connect() as conn:
            return conn.execute(
                "SELECT command, COUNT(*) FROM logs "
                "GROUP BY command ORDER BY COUNT(*) DESC"
            ).fetchall()

    def count_by_status(self):
        with self._connect() as conn:
            return conn.execute(
                "SELECT status, COUNT(*) FROM logs GROUP BY status"
            ).fetchall()

    def success_rate(self):
        with self._connect() as conn:
            total   = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
            success = conn.execute(
                "SELECT COUNT(*) FROM logs WHERE status IN ('Success','Captured')"
            ).fetchone()[0]
        return round(success / total * 100, 1) if total else 0.0

    def clear(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM logs")
            conn.commit()
