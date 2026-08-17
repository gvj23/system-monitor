from collections import deque
from typing import Optional
from datetime import datetime
import sqlite3
import json
import os

# ─────────────────────────────────────────
# IN-MEMORY (for live dashboard)
# ─────────────────────────────────────────
latest_metrics: Optional[dict] = None
last_seen: Optional[str] = None
cpu_history: deque = deque(maxlen=60)
connected_clients: list = []

# ─────────────────────────────────────────
# SQLITE SETUP (for history storage)
# ─────────────────────────────────────────
DB_PATH = "monitor.db"

def init_db():
    """Create tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            hostname TEXT,
            cpu_percent REAL,
            ram_percent REAL,
            disk_percent REAL,
            full_data TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def save_to_db(data: dict):
    """Save each metric snapshot to SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metrics 
            (timestamp, hostname, cpu_percent, ram_percent, disk_percent, full_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data["timestamp"],
            data["system"]["hostname"],
            data["cpu"]["usage_percent"],
            data["ram"]["usage_percent"],
            data["disk"]["usage_percent"],
            json.dumps(data)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ DB save error: {e}")

def get_db_history(limit: int = 100) -> list:
    """Get last N records from SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, hostname, cpu_percent, ram_percent, disk_percent
            FROM metrics
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": r[0],
                "hostname": r[1],
                "cpu": r[2],
                "ram": r[3],
                "disk": r[4]
            }
            for r in reversed(rows)
        ]
    except Exception as e:
        print(f"❌ DB read error: {e}")
        return []

# ─────────────────────────────────────────
# IN-MEMORY FUNCTIONS (for live updates)
# ─────────────────────────────────────────
def update_metrics(data: dict):
    global latest_metrics, last_seen
    latest_metrics = data
    last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update in-memory history (last 60 readings for live chart)
    cpu_history.append({
        "time": data["timestamp"],
        "cpu": data["cpu"]["usage_percent"],
        "ram": data["ram"]["usage_percent"],
    })

    # Also save to SQLite (permanent storage)
    save_to_db(data)

def get_latest() -> Optional[dict]:
    return latest_metrics

def get_cpu_history() -> list:
    return list(cpu_history)

def get_agent_status() -> str:
    if last_seen is None:
        return "offline"
    last = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S")
    diff = (datetime.now() - last).total_seconds()
    return "online" if diff <= 15 else "offline"

# Initialize DB when module loads
init_db()
