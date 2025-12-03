# threat_processor_opt.py
"""
Optimized threat processor with:
- DB setup and safe paths
- IOC insert / lookup
- scan_logs_and_alert (safe logging instead of sending real emails by default)
- demo data seeding
- optional AbuseIPDB remote lookup (only if ABUSEIPDB_KEY env var is set)
- query_ip_info() used by the web API
"""

import os
import sqlite3
import logging
import time
from typing import List, Tuple, Iterable, Optional, Dict, Any

# Base and DB path (absolute, reliable)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.getenv('TP_DB_FILE', os.path.join(BASE_DIR, 'db', 'threat_intel.db'))
EMAIL_LOG = os.getenv('TP_EMAIL_LOG', os.path.join(BASE_DIR, 'logs', 'email_alerts.log'))
LOG_FILE_DEFAULT = os.path.join(BASE_DIR, 'logs', 'access.log')

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


# -------------------------
# Database and IO helpers
# -------------------------
def ensure_dirs(db_path: str = DB_FILE, log_file: str = LOG_FILE_DEFAULT):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)


def setup_database(db_path: str = DB_FILE) -> None:
    """Create DB file and tables if missing."""
    ensure_dirs(db_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS iocs (
                ip_address TEXT PRIMARY KEY,
                abuse_confidence INTEGER,
                country_code TEXT,
                checked_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                abuse_confidence INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    logging.info("Database initialized at %s", db_path)


def insert_iocs(ioc_iter: Iterable[Tuple[str, int, str]], db_path: str = DB_FILE) -> int:
    """Insert or replace IOC records. Returns number processed."""
    ensure_dirs(db_path)
    inserted = 0
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for ip, confidence, country in ioc_iter:
            cur.execute(
                "INSERT OR REPLACE INTO iocs (ip_address, abuse_confidence, country_code, checked_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                (ip, int(confidence), country)
            )
            inserted += 1
        conn.commit()
    logging.info("Inserted/updated %d IOC records.", inserted)
    return inserted


def send_batch_email_alert(alerts: List[Tuple[str, int]], db_path: str = DB_FILE, email_log: str = EMAIL_LOG) -> None:
    """
    Safe 'email' function: appends alert details to a local log file.
    In production you can replace this with a real SMTP sender.
    """
    ensure_dirs(db_path, email_log)
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(email_log, 'a') as f:
            f.write(f"[{ts}] ALERT: {len(alerts)} malicious IP(s) detected\n")
            for ip, conf in alerts:
                f.write(f" - {ip} (confidence: {conf})\n")
        logging.info("Logged %d alerts to %s.", len(alerts), email_log)
    except Exception as e:
        logging.warning("Failed to write email log: %s", e)


# -------------------------
# Log scanning
# -------------------------
def scan_logs_and_alert(log_file: str = LOG_FILE_DEFAULT, db_path: str = DB_FILE) -> int:
    """
    Scans log_file for IPs, matches against IOC table (loaded into memory),
    writes matched alerts into alerts table, and logs alerts via send_batch_email_alert.
    Returns number of alerts detected.
    """
    ensure_dirs(db_path, log_file)

    if not os.path.exists(log_file):
        logging.warning("Log file '%s' not found.", log_file)
        return 0

    # load IOC map into memory
    ioc_map = {}
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT ip_address, abuse_confidence FROM iocs")
        for ip, conf in cur.fetchall():
            ioc_map[ip] = conf

    alerts = []
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            ip = line.strip()
            if not ip:
                continue
            if ip in ioc_map:
                alerts.append((ip, ioc_map[ip]))

    if not alerts:
        logging.info("No alerts detected.")
        return 0

    # batch insert alerts
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.executemany("INSERT INTO alerts (ip_address, abuse_confidence) VALUES (?, ?)", alerts)
        conn.commit()

    send_batch_email_alert(alerts, db_path=db_path)
    logging.info("Detected and recorded %d alerts.", len(alerts))
    return len(alerts)


# -------------------------
# Demo/demo-data helper
# -------------------------
def ensure_demo_data(db_path: str = DB_FILE, log_file: str = LOG_FILE_DEFAULT) -> None:
    """
    Create demo IOCs and a demo access.log if none are present.
    This is helpful for first-run automation in development environments.
    """
    ensure_dirs(db_path, log_file)
    # seed iocs if empty
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS iocs (ip_address TEXT PRIMARY KEY, abuse_confidence INTEGER, country_code TEXT, checked_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        cur.execute("SELECT COUNT(*) FROM iocs")
        count = cur.fetchone()[0] or 0
        if count == 0:
            demo = [
                ('192.168.1.1', 75, 'IN'),
                ('10.0.0.5', 62, 'US'),
                ('185.191.171.12', 90, 'GB'),
                ('206.189.123.45', 40, 'US'),
                ('8.8.8.8', 20, 'US')
            ]
            cur.executemany("INSERT OR REPLACE INTO iocs (ip_address, abuse_confidence, country_code) VALUES (?, ?, ?)", demo)
            conn.commit()
            logging.info("Seeded demo IOC data (%d rows).", len(demo))

    # create a demo access.log if missing or empty
    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        sample_ips = ["192.168.1.1", "10.0.0.5", "172.16.0.2", "185.191.171.12", "206.189.123.45", "8.8.8.8"]
        with open(log_file, 'w') as f:
            for _ in range(30):
                f.write(sample_ips[int(time.time()*1000) % len(sample_ips)] + "\n")
        logging.info("Created demo access log at %s", log_file)


# -------------------------
# Remote AbuseIPDB lookup (safe)
# -------------------------
def fetch_abuseipdb(ip: str) -> Optional[Dict[str, Any]]:
    """
    Query AbuseIPDB for 'ip' if ABUSEIPDB_KEY env var is set.
    Returns dict with keys: ip_address, abuse_confidence, country_code, or None on failure.
    """
    API_KEY = os.getenv('ABUSEIPDB_KEY', '').strip()
    if not API_KEY:
        logging.debug("ABUSEIPDB_KEY not set — skipping external lookup for %s", ip)
        return None

    try:
        import requests
    except Exception:
        logging.warning("requests module not available; cannot query AbuseIPDB.")
        return None

    try:
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {'Accept': 'application/json', 'Key': API_KEY}
        params = {'ipAddress': ip, 'maxAgeInDays': 90}
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        score = data.get('data', {}).get('abuseConfidenceScore')
        country = data.get('data', {}).get('countryCode')
        return {'ip_address': ip, 'abuse_confidence': int(score) if score is not None else 0, 'country_code': country}
    except Exception as e:
        logging.warning("fetch_abuseipdb failed for %s: %s", ip, e)
        return None


# -------------------------
# Query IP info (DB-first, then remote)
# -------------------------
def query_ip_info(ip: str, db_path: str = DB_FILE) -> Dict[str, Any]:
    """
    Return info for 'ip'.
    Flow:
      1) Try DB for IOC and recent alerts.
      2) If not in DB and ABUSEIPDB_KEY set -> fetch remote, store and return.
      3) If remote unavailable -> return demo result or helpful error.
    """
    ip = (ip or "").strip()
    if not ip:
        return {'found': False, 'error': 'empty ip'}

    ensure_dirs(db_path)

    # 1) Query DB
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT ip_address, abuse_confidence, country_code FROM iocs WHERE ip_address = ?", (ip,))
        row = cur.fetchone()
        if row:
            ioc = {'ip_address': row[0], 'abuse_confidence': row[1], 'country_code': row[2], 'source': 'db'}
            cur.execute("SELECT id, timestamp, abuse_confidence FROM alerts WHERE ip_address = ? ORDER BY timestamp DESC LIMIT 10", (ip,))
            alerts = [{'id': r[0], 'timestamp': r[1], 'abuse_confidence': r[2]} for r in cur.fetchall()]
            return {'found': True, 'ioc': ioc, 'alerts': alerts}

    # 2) Try remote AbuseIPDB
    remote = fetch_abuseipdb(ip)
    if remote:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO iocs (ip_address, abuse_confidence, country_code, checked_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                        (remote['ip_address'], remote['abuse_confidence'], remote['country_code']))
            conn.commit()
        remote['source'] = 'abuseipdb'
        return {'found': True, 'ioc': remote, 'alerts': []}

    # 3) Demo fallback (development)
    demo_map = {
        '192.168.1.1': {'abuse_confidence': 75, 'country_code': 'IN'},
        '10.0.0.5': {'abuse_confidence': 62, 'country_code': 'US'},
        '185.191.171.12': {'abuse_confidence': 90, 'country_code': 'GB'},
    }
    if ip in demo_map:
        demo = demo_map[ip]
        return {'found': True, 'ioc': {'ip_address': ip, 'abuse_confidence': demo['abuse_confidence'], 'country_code': demo['country_code'], 'source': 'demo'}, 'alerts': []}

    return {'found': False, 'error': 'No data found locally and external lookup unavailable (set ABUSEIPDB_KEY to enable)'}
