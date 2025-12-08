#!/bin/bash
#
# ransom_decrypt.sh
# Decryption script for the ransomware simulation lab.
# - Decrypts all *.locked files in the target directory
# - Restores original filenames
#

set -e

# ================== CONFIG ==================
TARGET_DIR="${1:-/home/ubuntu/victim_data}"   # Same directory used during encryption
PASSPHRASE="infected123"                      # Must match ransom_sim.sh
# ============================================

if [ ! -d "$TARGET_DIR" ]; then
  echo "[!] Target directory does not exist: $TARGET_DIR"
  exit 1
fi

echo "[*] Starting decryption in: $TARGET_DIR"

shopt -s nullglob
LOCKED_FILES=("$TARGET_DIR"/*.locked)

if [ ${#LOCKED_FILES[@]} -eq 0 ]; then
  echo "[!] No .locked files found in $TARGET_DIR"
  exit 0
fi

for file in "${LOCKED_FILES[@]}"; do
  if [ -f "$file" ]; then
    original="${file%.locked}"
    echo "[*] Decrypting: $file -> $original"
    openssl enc -d -aes-256-cbc -in "$file" -out "$original" -k "$PASSPHRASE"
    rm -f "$file"
  fi
done

echo "[+] Decryption complete."
echo "[+] Current contents of $TARGET_DIR:"
ls -l "$TARGET_DIR"
