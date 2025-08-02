import os
import sys
import sqlite3
import json
from openpyxl import Workbook

# Ensure the script can be run standalone by adjusting the import path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import init_db, DB_PATH
from config import EXPORT_PATH

def export_to_xls():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, formats, best_sellers_rank, url, datestamp FROM listings")
    rows = c.fetchall()
    conn.close()

    max_formats = 0
    max_ranks = 0
    parsed_rows = []
    for row in rows:
        title, formats, best_sellers_rank, url, datestamp = row
        try:
            formats_list = json.loads(formats) if formats else []
        except Exception:
            formats_list = []
        try:
            ranks_list = json.loads(best_sellers_rank) if best_sellers_rank else []
        except Exception:
            ranks_list = []
        max_formats = max(max_formats, len(formats_list))
        max_ranks = max(max_ranks, len(ranks_list))
        parsed_rows.append((title, formats_list, ranks_list, url, datestamp))

    wb = Workbook()
    ws = wb.active
    ws.title = "Listings"

    header = ["Title"]
    for i in range(max_formats):
        header.append(f"Format {i+1}")
        header.append(f"Price {i+1}")
    for i in range(max_ranks):
        header.append(f"Category {i+1}")
        header.append(f"Rank {i+1}")
    header.append("URL")
    header.append("Datestamp")
    ws.append(header)

    for title, formats_list, ranks_list, url, datestamp in parsed_rows:
        row = [title]
        for i in range(max_formats):
            if i < len(formats_list):
                fmt = formats_list[i]
                row.append(fmt.get("format", "") if isinstance(fmt, dict) else "")
                row.append(fmt.get("price", "") if isinstance(fmt, dict) else "")
            else:
                row.extend(["", ""])
        for i in range(max_ranks):
            if i < len(ranks_list):
                rank = ranks_list[i]
                row.append(rank.get("category", "") if isinstance(rank, dict) else "")
                row.append(rank.get("rank", "") if isinstance(rank, dict) else "")
            else:
                row.extend(["", ""])
        row.append(url)
        row.append(datestamp)
        ws.append(row)

    wb.save(EXPORT_PATH)
    print(f"[DB] Exported {len(rows)} rows to {EXPORT_PATH}")

if __name__ == "__main__":
    export_to_xls()
