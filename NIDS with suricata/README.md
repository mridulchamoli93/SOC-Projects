# Group 2 Internship — Infotact Solutions

# Suricata + PHP Test Lab

A small, reproducible lab to run **Suricata IDS** against a couple of PHP webpages and quickly generate test traffic (SQLi/XSS/malware download/Telnet/FTP/etc.).

This README gives you **two ways** to set up and run the lab:

1. **Automated** — run a single script to install, configure, and start everything.
2. **Manual** — step‑by‑step commands you can copy/paste.

> ⚠️ For education and testing **on your own systems only**. Don’t run these tests against networks or hosts you don’t own/operate.

---

## Repo Structure

```
.
├─ suricata/
│  └─ local.rules           # Your custom Suricata rules
├─ web/
│  ├─ index.php             # Your PHP pages (examples)
│  ├─ login.php
│  ├─ dashboard.php
│  └─ run.php
├─ scripts/
│  └─ setup.sh              # Automation script (rename here if different)
├─ commands.txt             # Test-traffic cheat sheet
└─ README.md
```

> If your file/dir names differ, adjust paths below accordingly (especially the automation script name).

---

## Requirements

* OS: Ubuntu/Debian/Kali family recommended
* Root privileges (or `sudo`) for network capture and service management
* Packages: `suricata`, `apache2`, `php`, `libapache2-mod-php`, `mysql-server` (or `mariadb-server`)

---

# 1) Automated Setup

The automation script will:

* Install required packages
* Copy `suricata/local.rules` to `/etc/suricata/rules/local.rules`
* Ensure Suricata loads `local.rules` and basic variables are sane (`HOME_NET`)
* Copy PHP files from `web/` to `/var/www/html/`
* Enable & start `suricata`, `apache2`, and `mysql`
* Optionally select the capture interface (`lo`, `wlan0`, `eth0`, etc.)

### 1.1 Run the script

```bash
# From repo root
chmod +x ./scripts/setup.sh
sudo ./scripts/setup.sh --iface wlan0   # use wlan0, or
sudo ./scripts/setup.sh --iface lo      # for localhost-only testing
```

**Notes**

* You must run as **root** (use `sudo`). Packet capture requires elevated privileges.
* If your script uses env vars instead of flags, you can do: `sudo IFACE=wlan0 ./scripts/setup.sh`.
* If your script has a different filename or path, replace `./scripts/setup.sh` accordingly.

### 1.2 Verify services

```bash
sudo systemctl status suricata
sudo systemctl status apache2
sudo systemctl status mysql
```

### 1.3 Check Suricata logs

```bash
# High-level alerts
sudo tail -f /var/log/suricata/fast.log

# JSON event stream (optional)
sudo tail -f /var/log/suricata/eve.json
```

---

# 2) Manual Setup (copy/paste friendly)

## 2.1 Install packages

```bash
sudo apt update
sudo apt install -y suricata apache2 php libapache2-mod-php mysql-server
```

(Use `mariadb-server` instead of `mysql-server` if that’s your distro default.)

## 2.2 Copy your files

```bash
# Suricata rules
sudo mkdir -p /etc/suricata/rules
sudo cp ./suricata/local.rules /etc/suricata/rules/local.rules

# PHP application
sudo cp -r ./web/* /var/www/html/

# Permissions for web root (optional; adjust if you keep other content there)
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

## 2.3 Configure Suricata

Open `/etc/suricata/suricata.yaml` and confirm these two things:

1. **Rules path and inclusion**

```yaml
# Make sure the default rule path points to /etc/suricata/rules
default-rule-path: /etc/suricata/rules

# Ensure local.rules is listed under rule-files
rule-files:
  - local.rules
```

2. **HOME\_NET / EXTERNAL\_NET** (optional but recommended for accurate alerts)

```yaml
vars:
  address-groups:
    # For localhost-only testing
    # HOME_NET: "[127.0.0.1]"

    # For a typical home/lab subnet
    # HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"

    # Keep defaults if you prefer (often fine for a lab)
```

Validate the config:

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v
```

## 2.4 Start and enable services

```bash
# Enable + start via systemd
sudo systemctl enable suricata
sudo systemctl start suricata

sudo systemctl enable apache2
sudo systemctl start apache2

sudo systemctl enable mysql
sudo systemctl start mysql
```

**Alternative:** Run Suricata directly against an interface (foreground):

```bash
# Wireless interface
sudo suricata -c /etc/suricata/suricata.yaml -i wlan0

# Localhost loopback (same box hitting its own web server)
sudo suricata -c /etc/suricata/suricata.yaml -i lo
```

> 💡 Which interface should I use?
>
> * **lo** → you’re testing from the same machine using `http://127.0.0.1/`.
> * **wlan0/eth0** → you’ll hit the web server from another device on the network, or you want to see real on‑wire traffic.
>
> List your interfaces with: `ip -brief a`

## 2.5 Watch logs

```bash
sudo tail -f /var/log/suricata/fast.log
```

You should see alerts when you run the test commands below.

---

# 3) Generate Test Traffic

The repo includes `commands.txt` with curl/Telnet/FTP/DNS examples that commonly trigger IDS rules. You can run these from the Suricata host itself or another machine on the same LAN.

> Replace `127.0.0.1` with your server IP when testing over `wlan0/eth0`.

```bash
# DNS lookup to a suspicious domain (example)
dig evil.com

# Legacy cleartext protocols
telnet 127.0.0.1 23
ftp 127.0.0.1
nc 127.0.0.1 21

# Web requests to trigger common signatures
curl -A "Mozilla" "http://127.0.0.1/dashboard.php?test=password"
curl -A "sqlmap" http://127.0.0.1/

# Try command/data injection patterns
curl -d "/bin/bash" http://127.0.0.1/

# Basic SQLi probes
curl "http://127.0.0.1/login.php?id=1 UNION SELECT 1,2,3"
curl "http://127.0.0.1/login.php?id=1 OR 1=1"

# Reflected XSS probe
curl -d "<script>alert(1)</script>" http://127.0.0.1/

# Simulate a malware download (will just fetch a file name if your server serves it)
curl -o test.exe http://127.0.0.1/malware.exe

# PowerShell beacon-like query path
curl "http://127.0.0.1/run.php?powershell=encodedCommand"
```

As you run these, keep an eye on:

```bash
sudo tail -f /var/log/suricata/fast.log
```

If your `local.rules` contains SSH/ICMP/Telnet/FTP/SQLi/XSS/UA signatures, you should see hits. Tweak rules or payloads as needed to exercise specific detections.

---

# 4) Troubleshooting

**No alerts in `fast.log`**

* Confirm you’re monitoring the correct interface (`lo` vs `wlan0/eth0`).
* Ensure `local.rules` is actually loaded (see `rule-files` in `suricata.yaml`).
* Validate config: `sudo suricata -T -c /etc/suricata/suricata.yaml -v`.
* If running via systemd, check: `sudo journalctl -u suricata -e`.

**Apache running but site unreachable**

* Test locally: `curl -I http://127.0.0.1/` on the server itself.
* Check firewall (e.g., `ufw status`) and that Apache is listening on `:80` (`sudo ss -ltnp | grep :80`).

**Permission issues when copying files**

* Use `sudo` when writing to `/etc/suricata/` and `/var/www/html/`.
* Ensure web root is readable by `www-data`.

**Which IP to use from another device?**

* Find server IP: `ip -brief a` (look for `wlan0` or `eth0`).
* Then browse: `http://<server-ip>/` from the other device.

---

# 5) Uninstall / Reset (optional)

```bash
# Stop services
sudo systemctl stop suricata apache2 mysql

# Remove packages (keeps configs unless you use purge)
sudo apt remove -y suricata apache2 php libapache2-mod-php mysql-server

# Purge configs (destructive)
sudo apt purge -y suricata apache2 php libapache2-mod-php mysql-server

# Clean up rules and web files if they only belong to this lab
sudo rm -f /etc/suricata/rules/local.rules
sudo rm -f /var/www/html/{index.php,login.php,dashboard.php,run.php}
```

---

## Contributing

PRs welcome—add rules, more PHP endpoints, or additional test cases.

## License

All rights are reserved to Thanatos Groups.
