#!/bin/bash
#
# generate_test_data.sh
# Creates a demo "victim" directory with fake sensitive files.
#

set -e

VICTIM_DIR="${1:-/home/ubuntu/victim_data}"

echo "[*] Creating victim directory at: $VICTIM_DIR"
mkdir -p "$VICTIM_DIR"

echo "[*] Generating sample files..."
echo "Fake bank account data"        > "$VICTIM_DIR/account.txt"
echo "Dummy password list"           > "$VICTIM_DIR/passwords.txt"
echo "Client records (demo only)"    > "$VICTIM_DIR/clients.txt"
echo "HR confidential (fake data)"   > "$VICTIM_DIR/hr.txt"

echo "[+] Test data created:"
ls -l "$VICTIM_DIR"
