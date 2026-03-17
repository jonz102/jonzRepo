from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

from flask import Flask, g, redirect, render_template, request, url_for, abort


APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "scoreboard.db"

# Default configuration
DEFAULT_NAMES = os.getenv("NAMES", "Jonny,Tina,Avinash").split(",")
DEFAULT_CATEGORIES = [int(x) for x in os.getenv("CATEGORIES", "1,2,3,4,5,6").split(",")]


def create_app() -> Flask:
    app = Flask(__name__)

    @app.before_request
    def before_request() -> None:
        g.db = get_db()

    @app.teardown_request
    def teardown_request(exc: BaseException | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.route("/")
    def index():
        names = get_names()
        categories = get_categories()
        counts = fetch_counts(names, categories)
        return render_template(
            "index.html",
            names=names,
            categories=categories,
            counts=counts,
        )

    @app.post("/increment")
    def increment():
        user = request.form.get("user")
        category = request.form.get("category", type=int)
        if not user or category is None:
            abort(400, "Missing user or category")
        increment_count(user, category)
        value = get_value(user, category)

        # If called via HTMX, return the small snippet for the cell value
        if request.headers.get("HX-Request") == "true":
            return render_template("_cell.html", user=user, category=category, value=value)
        return redirect(url_for("index"))

    @app.post("/reset")
    def reset():
        reset_counts()
        return redirect(url_for("index"))

    ensure_db()
    return app


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db() -> None:
    first_time = not DB_PATH.exists()
    conn = get_db()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS counts (
                user TEXT NOT NULL,
                category INTEGER NOT NULL,
                value INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user, category)
            )
            """
        )
    conn.close()
    if first_time:
        initialize_defaults()


def initialize_defaults() -> None:
    names = get_names()
    categories = get_categories()
    conn = get_db()
    with conn:
        for name in names:
            for cat in categories:
                conn.execute(
                    "INSERT OR IGNORE INTO counts(user, category, value) VALUES (?, ?, 0)",
                    (name, cat),
                )
    conn.close()


def get_names() -> List[str]:
    return [n.strip() for n in DEFAULT_NAMES if n.strip()]


def get_categories() -> List[int]:
    return DEFAULT_CATEGORIES


def fetch_counts(names: List[str], categories: List[int]) -> Dict[Tuple[str, int], int]:
    placeholders = ",".join(["?"] * len(names))
    cat_placeholders = ",".join(["?"] * len(categories))
    params = [*names, *categories]
    conn = get_db()
    rows = conn.execute(
        f"SELECT user, category, value FROM counts WHERE user IN ({placeholders}) AND category IN ({cat_placeholders})",
        params,
    ).fetchall()
    values: Dict[Tuple[str, int], int] = {(r["user"], r["category"]): r["value"] for r in rows}

    # Ensure missing combinations are present as zero
    for name in names:
        for cat in categories:
            values.setdefault((name, cat), 0)
    return values


def increment_count(user: str, category: int) -> None:
    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO counts(user, category, value) VALUES (?, ?, 1) ON CONFLICT(user, category) DO UPDATE SET value = value + 1",
            (user, category),
        )


def get_value(user: str, category: int) -> int:
    conn = get_db()
    row = conn.execute(
        "SELECT value FROM counts WHERE user = ? AND category = ?",
        (user, category),
    ).fetchone()
    return int(row["value"]) if row else 0


def reset_counts() -> None:
    conn = get_db()
    with conn:
        conn.execute("UPDATE counts SET value = 0")


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)