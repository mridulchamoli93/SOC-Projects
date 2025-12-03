# app.py
"""
Main Flask entrypoint for Thanatos (Threat Intel Dashboard).

Usage:
    python app.py

This app expects:
- templates/dashboard.html  (Jinja template)
- static/style.css          (dashboard styling)
- threat_processor_opt.py   (contains DB functions: setup_database, ensure_demo_data, query_ip_info, scan_logs_and_alert)
- dashboard_opt.py          (contains fetch_dashboard_data)

Environment (optional):
- ABUSEIPDB_KEY  (if present, remote lookups will be enabled)
- TP_DB_FILE     (override DB file path)
"""

import os
import threading
import logging
from flask import Flask, render_template, jsonify, request

# Try to load .env quietly (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Import our optimized modules (must be present in project root)
import threat_processor_opt as tp
import dashboard_opt as dh

# --------------------------
# Configuration & paths
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.getenv('TP_DB_FILE', os.path.join(BASE_DIR, 'db', 'threat_intel.db'))
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'access.log')

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# --------------------------
# Flask app
# --------------------------
app = Flask(__name__, static_folder='static', template_folder='templates')

# On startup: make sure DB and demo data exist
tp.setup_database(DB_FILE)
# ensure_demo_data will create sample IOC rows and a demo access.log if needed.
tp.ensure_demo_data(db_path=DB_FILE, log_file=LOG_FILE)

# Background scan lock to prevent concurrent scans
_scan_lock = threading.Lock()


def _run_scan_background():
    """Run the scanner with a lock to avoid concurrent runs."""
    with _scan_lock:
        logging.info("Background scan started.")
        try:
            tp.scan_logs_and_alert(log_file=LOG_FILE, db_path=DB_FILE)
        except Exception as e:
            logging.exception("Error during background scan: %s", e)
        logging.info("Background scan finished.")


# --------------------------
# Routes
# --------------------------
@app.route("/")
def index():
    """Render the dashboard page with initial data injected."""
    data = dh.fetch_dashboard_data(db_path=DB_FILE)
    return render_template("dashboard.html", iocs=data['iocs'], alerts=data['alerts'])


@app.route("/api/data")
def api_data():
    """Return JSON payload used by frontend polling (iocs and alerts)."""
    data = dh.fetch_dashboard_data(db_path=DB_FILE)
    return jsonify(data)


@app.route("/run_now", methods=["POST", "GET"])
def run_now():
    """
    Trigger a background scan. Returns immediately.
    Frontend uses this to kick off scanning without blocking.
    """
    try:
        t = threading.Thread(target=_run_scan_background, daemon=True)
        t.start()
        return jsonify({"status": "scan started"})
    except Exception as e:
        logging.exception("Failed to start background scan: %s", e)
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/query_ip", methods=["POST"])
def api_query_ip():
    """
    Query an IP from UI:
    POST JSON { "ip": "1.2.3.4" }
    Response: { found: bool, ioc: {...}, alerts: [...], error: optional }
    """
    payload = request.get_json(force=True, silent=True) or {}
    ip = (payload.get('ip') or payload.get('q') or request.form.get('ip') or "").strip()
    if not ip:
        return jsonify({'found': False, 'error': 'Missing ip parameter'}), 400

    try:
        result = tp.query_ip_info(ip, db_path=DB_FILE)
        return jsonify(result)
    except Exception as e:
        logging.exception("Error in query_ip_info for %s: %s", ip, e)
        return jsonify({'found': False, 'error': str(e)}), 500


# --------------------------
# Health / debug endpoints (optional)
# --------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "db": os.path.exists(DB_FILE), "log": os.path.exists(LOG_FILE)})


# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    logging.info("Starting Thanatos Flask app")
    logging.info("DB file: %s", DB_FILE)
    logging.info("Log file: %s", LOG_FILE)
    # For local development use debug=True; disable in production
    app.run(debug=True, host="0.0.0.0", port=5000)
