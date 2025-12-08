# 🔴 End-to-End Ransomware Detection & Incident Response Lab  


---

## 📌 Project Overview

This project demonstrates a **full real-world ransomware attack simulation**, including:

- Adversary emulation  
- Linux persistence via cron  
- Ransomware-style file encryption  
- SIEM log ingestion  
- Detection engineering  
- Automated alerting  
- Incident response & recovery  

Everything is executed in a **controlled SOC lab environment** and detected using **real Splunk SIEM alerts**.

This project is built to reflect **Tier-1 / Tier-2 SOC analyst operations**.

---

## 🏗️ Lab Architecture

**Attacker Machine**
- Kali Linux  
- CALDERA Server  

**Victim Machine**
- Ubuntu 22.04  
- Sandcat Agent  
- Splunk Universal Forwarder  

**SIEM**
- Splunk Enterprise  

**Log Flow**
Ubuntu → Splunk Forwarder → Splunk SIEM

yaml
Copy code

---

## ⚔️ Attack Simulation Breakdown

| Phase | Description | MITRE ID |
|--------|------------|----------|
| Initial Access | Sandcat agent deployed via CALDERA | T1059 |
| Persistence | Root cron job executes payload every minute | T1053 |
| Impact | Files encrypted using OpenSSL & ransom note dropped | T1486 |

---

## 🧪 Ransomware Simulation Scripts

Located in the `scripts/` folder:

| Script | Purpose |
|--------|----------|
| `generate_test_data.sh` | Creates fake sensitive victim files |
| `ransom_sim.sh` | Encrypts victim files & drops ransom note |
| `ransom_decrypt.sh` | Restores encrypted files |

---

## 🔍 Detection Engineering (Splunk Queries)

### ✅ Cron Persistence Detection – T1053
```spl
index=* host=ubantu "CRON" "persistence-active"
Detects:

Root cron execution

Scheduled persistence abuse

✅ Ransomware Activity Detection – T1486
spl
Copy code
index=* host=ubantu ("README_RESTORE" OR ".locked" OR "openssl")
Detects:

File encryption activity

Ransom note artifacts

Cryptographic behavior

🚨 Real-Time Alerts Implemented
Alert Name	Technique
Suspicious Root Cron Persistence	T1053
Potential Ransomware Encryption Activity	T1486

Both alerts are:

✅ Real-time

✅ Trigger if results > 0

✅ SOC operational grade

📂 Evidence & Screenshots
All proof-of-work screenshots are located in:

bash
Copy code
/screenshots
This includes:

CALDERA agent connection

Live operations

Cron persistence execution

Splunk detections

Alert creation

Log ingestion

A full explanation for each screenshot is available in:

bash
Copy code
/screenshots/README.md
📑 Incident Response Report
A complete SOC-style incident response report is available here:

bash
Copy code
/report/Incident_Response_Report.pdf
It includes:

Executive summary

Attack timeline

Detection logic

Indicators of compromise

Containment & eradication

Recovery

Lessons learned

MITRE mapping

✅ Skills Demonstrated
SIEM Log Ingestion & Correlation

Linux Threat Detection

Ransomware Behavioral Analysis

Privilege Escalation & Persistence Detection

Detection Engineering (SPL)

Automated Alerting

Incident Response Workflow

MITRE ATT&CK Mapping

SOC L1 / L2 Operations

🏁 Final Outcome
This project provides real SOC proof-of-work, not theoretical simulations.
It demonstrates an attacker-to-defender lifecycle using production-grade detection logic and automation.

This lab is suitable evidence for:

SOC Analyst (Tier 1 / Tier 2)

Detection Engineer (Junior)

Blue Team / DFIR internships

⚠️ Disclaimer
This project is strictly for educational and defensive security purposes only.
All attacks were performed in a controlled lab environment with no real-world systems affected.

📬 Author
Mridul
Aspiring SOC Analyst | Blue Team
Tools: Splunk, Linux, CALDERA, MITRE ATT&CK
