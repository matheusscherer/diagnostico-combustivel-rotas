from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def save_run(db_path: Path, summary: dict[str, Any]) -> int:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                critical_deviation_pct REAL NOT NULL,
                summary_json TEXT NOT NULL
            )
            """
        )
        cursor = connection.execute(
            """
            INSERT INTO analysis_runs (
                created_at, critical_deviation_pct, summary_json
            ) VALUES (?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                summary["desvio_critico_pct"],
                json.dumps(summary, ensure_ascii=False, allow_nan=False),
            ),
        )
        return int(cursor.lastrowid)


def list_recent_runs(db_path: Path, limit: int = 20) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("limit deve ser maior que zero")

    db_path = Path(db_path)
    if not db_path.exists():
        return []

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, created_at, critical_deviation_pct, summary_json
            FROM analysis_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "critical_deviation_pct": row["critical_deviation_pct"],
            "summary": json.loads(row["summary_json"]),
        }
        for row in rows
    ]
