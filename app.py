import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "lucky_draw.db"))

PRIZES = [
    {"key": "discount15", "label": "15% Discount", "limit": 6},
    {"key": "discount10", "label": "10% Discount", "limit": 10},
    {"key": "discount5", "label": "5% Discount", "limit": 20},
    {"key": "earrings", "label": "Free Earrings", "limit": 20},
    {"key": "tlight", "label": "Free T-light Holder", "limit": 30},
]

def connect():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS prize_counts (
            prize_key TEXT PRIMARY KEY,
            count INTEGER NOT NULL DEFAULT 0
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS draw_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prize_key TEXT NOT NULL,
            drawn_at TEXT NOT NULL
        )""")
        for prize in PRIZES:
            conn.execute("INSERT OR IGNORE INTO prize_counts(prize_key, count) VALUES (?, 0)", (prize["key"],))

def current_counts(conn):
    rows = {r["prize_key"]: r["count"] for r in conn.execute("SELECT prize_key, count FROM prize_counts")}
    return [
        {**p, "used": rows.get(p["key"], 0), "remaining": p["limit"] - rows.get(p["key"], 0)}
        for p in PRIZES
    ]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    with connect() as conn:
        counts = current_counts(conn)
        return jsonify({"prizes": counts, "total_used": sum(p["used"] for p in counts),
                        "total_limit": sum(p["limit"] for p in counts)})

@app.route("/api/draw", methods=["POST"])
def draw():
    import random
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        counts = current_counts(conn)
        available = [p for p in counts if p["remaining"] > 0]
        if not available:
            return jsonify({"error": "All 86 offers have been used. Ask the admin to reset the draw."}), 409
        # Weighted by remaining quantity, so each of the 86 total offers has an equal chance.
        selected = random.choices(available, weights=[p["remaining"] for p in available], k=1)[0]
        conn.execute("UPDATE prize_counts SET count = count + 1 WHERE prize_key = ?", (selected["key"],))
        conn.execute("INSERT INTO draw_log(prize_key, drawn_at) VALUES (?, ?)",
                     (selected["key"], datetime.utcnow().isoformat(timespec="seconds") + "Z"))
        counts_after = current_counts(conn)
        return jsonify({"prize": selected["label"], "prizes": counts_after,
                        "total_used": sum(p["used"] for p in counts_after),
                        "total_limit": sum(p["limit"] for p in counts_after)})

@app.route("/api/reset", methods=["POST"])
def reset():
    # Simple admin PIN; change this before publishing.
    expected_pin = os.environ.get("ADMIN_PIN", "2468")
    supplied_pin = str((request.get_json(silent=True) or {}).get("pin", ""))
    if supplied_pin != expected_pin:
        return jsonify({"error": "Incorrect admin PIN."}), 403
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE prize_counts SET count = 0")
        conn.execute("DELETE FROM draw_log")
        return jsonify({"message": "All offers have been reset to zero."})

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
