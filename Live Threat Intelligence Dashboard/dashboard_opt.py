# dashboard_opt.py
"""
Lightweight dashboard helper.
Provides a function to fetch latest IOCs and Alerts for the UI.
DO NOT include HTML here — only Python logic.
"""

import sqlite3
import os
from typing import Dict, List

# Absolute DB path ensures no "unable to open database file" errors
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "db", "threat_intel.db")


def fetch_dashboard_data(
    db_path: str = DB_FILE,
    ioc_limit: int = 50,
    alerts_limit: int = 50
) -> Dict[str, List[dict]]:
    """
    Return dashboard data:
    {
        'iocs': [...],
        'alerts': [...]
    }
    """

    # If DB doesn't exist yet, return empty result (UI won't crash)
    if not os.path.exists(db_path):
        return {"iocs": [], "alerts": []}

    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Fetch IOCs
            cur.execute(
                """
                SELECT ip_address, abuse_confidence, country_code
                FROM iocs
                ORDER BY abuse_confidence DESC
                LIMIT ?
                """,
                (ioc_limit,)
            )
            iocs = [dict(row) for row in cur.fetchall()]

            # Fetch latest alerts
            cur.execute(
                """
                SELECT id, ip_address, abuse_confidence, timestamp
                FROM alerts
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (alerts_limit,)
            )
            alerts = [dict(row) for row in cur.fetchall()]

            return {"iocs": iocs, "alerts": alerts}

    except Exception as e:
        # On error, still return a safe structure
        return {"iocs": [], "alerts": [], "error": str(e)}


# Debug preview when running directly:
if __name__ == "__main__":
    print(fetch_dashboard_data())
