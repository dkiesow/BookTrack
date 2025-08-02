import sqlite3
import json
from datetime import datetime
from config import DB_PATH

def init_db():
    print("[DB] Initializing database and ensuring listings table exists...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            formats TEXT,
            best_sellers_rank TEXT,
            url TEXT,
            datestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Database initialized.")

def save_listing(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    datestamp = datetime.now().isoformat(timespec="seconds")
    c.execute("""
        INSERT INTO listings (title, formats, best_sellers_rank, url, datestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["title"],
        json.dumps(data["formats"]),
        json.dumps(data["best_sellers_rank"]),
        data["url"],
        datestamp
    ))
    conn.commit()
    conn.close()
    print("[DB] Listing saved successfully.")
