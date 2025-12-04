#!/bin/bash
# Thanatos Suricata Installer & Rules Deployer

# Check root
if [[ $EUID -ne 0 ]]; then
   echo "Please run as root"
   exit 1
fi

# Display Thanatos banner
if command -v figlet >/dev/null 2>&1; then
    figlet -f slant "Thanatos"
else
    echo "####################################"
    echo "#         THANATOS SURICATA        #"
    echo "####################################"
fi

# Ask for distro to install suricata properly
echo "Which Linux distro are you using?"
select distro in "Debian/Ubuntu" "Fedora/RHEL" "Arch" "Quit"; do
    case $distro in
        "Debian/Ubuntu")
            PKG_INSTALL="apt update && apt install -y suricata git curl figlet"
            break
            ;;
        "Fedora/RHEL")
            PKG_INSTALL="dnf install -y suricata git curl figlet"
            break
            ;;
        "Arch")
            PKG_INSTALL="pacman -Syu --noconfirm suricata git curl figlet"
            break
            ;;
        "Quit")
            exit 0
            ;;
        *)
            echo "Invalid option $REPLY"
            ;;
    esac
done

# Variables
RULES_URL="https://github.com/Abhims898/Project-1---Network-Intrusion-Detection-System-NIDS-Rule-Creation-and-Testing-Labunder-progress/blob/main/local.rules"
YAML_URL="https://github.com/Abhims898/Project-1---Network-Intrusion-Detection-System-NIDS-Rule-Creation-and-Testing-Labunder-progress/blob/main/suricata.yaml"
RULES_DIR="/etc/suricata/rules"
CONFIG_FILE="/etc/suricata/suricata.yaml"
BACKUP_DIR="/etc/suricata/backup_$(date +%F_%T)"

# Install Suricata
echo "[*] Installing Suricata..."
eval $PKG_INSTALL

# Backup existing configs
mkdir -p "$BACKUP_DIR"
cp -r "$RULES_DIR" "$BACKUP_DIR/" 2>/dev/null
cp "$CONFIG_FILE" "$BACKUP_DIR/" 2>/dev/null

# Download rules and config
echo "[*] Downloading custom rules and config..."
mkdir -p "$RULES_DIR"
curl -L "$RULES_URL" -o "$RULES_DIR/local.rules"
curl -L "$YAML_URL" -o "$CONFIG_FILE"

# Detect interfaces and choose HOME_NET
echo "[*] Detecting network interfaces..."
IFS=$'\n' read -r -d '' -a IFACES < <(ip -o addr show up primary scope global | awk '{print $2 " - " $4}' && printf '\0')

echo "Available interfaces with IPs:"
for i in "${!IFACES[@]}"; do
    echo "$i) ${IFACES[$i]}"
done
read -p "Select interface number to use as HOME_NET: " IFACE_NUM
SELECTED_IFACE_IP=$(echo "${IFACES[$IFACE_NUM]}" | awk '{print $3}' | cut -d/ -f1)
echo "[*] Selected IP $SELECTED_IFACE_IP as HOME_NET"

# Update HOME_NET in suricata.yaml automatically
sed -i "s|\$HOME_NET|[$SELECTED_IFACE_IP]|g" "$CONFIG_FILE"

# Test configuration
echo "[*] Testing Suricata config..."
suricata -T -c "$CONFIG_FILE" -v

# Start Suricata
echo "[*] Starting Suricata in daemon mode..."
systemctl restart suricata || suricata -c "$CONFIG_FILE" -i lo -D

# Verify rules loaded
echo "[*] Verifying loaded rules..."
LOADED_RULES=$(suricata -c "$CONFIG_FILE" -S "$RULES_DIR/local.rules" --runmode test | grep -i "Loaded rules")
echo "[✓] $LOADED_RULES"

echo "[✓] Suricata is ready to use!"
