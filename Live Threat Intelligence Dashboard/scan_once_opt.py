"""Optimized scan_once script that uses the optimized threat_processor module."""
from threat_processor_opt import scan_logs_and_alert

def main():
    count = scan_logs_and_alert(log_file='logs/access.log', db_path='db/threat_intel.db')
    print(f"[scan_once] Alerts detected: {count}")

if __name__ == '__main__':
    main()