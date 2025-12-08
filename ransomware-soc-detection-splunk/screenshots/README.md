# 📸 Project Screenshots – Evidence & Validation

This folder contains visual proof of the full ransomware attack simulation, detection engineering, and SOC response workflow executed in this project. Each screenshot validates a real-world security operation step.

---

## 1️⃣ CALDERA Agent Connected (Initial Access)

**File:** `project.png`  
✅ Confirms successful deployment of the Sandcat agent on the Ubuntu victim  
✅ Shows:
- Host: `ubantu`
- Platform: Linux
- Privilege: Elevated
- Status: Alive & Trusted  

This validates **Initial Access & C2 Connectivity**.

---

## 2️⃣ Sandcat Agent Beacon (Command Execution)

**File:** `project1.png`  
✅ Shows the agent beaconing back to the CALDERA server  
✅ Confirms:
- HTTP communication channel
- Group assignment (`red`)
- Successful instruction execution  

Mapped to **MITRE T1059 – Command Execution**.

---

## 3️⃣ Running Live CALDERA Operation

**File:** `project3.png`  
✅ Live operation view showing:
- Active agent
- Command execution timeline
- Successful command outputs  

This proves real **adversary emulation in action**.

---

## 4️⃣ Cron Persistence Execution on Victim

**File:** `project4.png`  
✅ Live terminal output showing:

## persistence-active

running repeatedly from `/tmp/persist.log`  
✅ Confirms root-level scheduled execution  

Mapped to **MITRE T1053 – Scheduled Task / Cron Persistence**.

---

## 5️⃣ Ubuntu Logs Streaming to Splunk SIEM

**File:** `project5.png`  
✅ Confirms:
- `/var/log/syslog` ingestion
- Host = `ubantu`
- Sourcetype = `syslog`  
✅ Proves:
Real-time **log forwarding from victim to SIEM**.

---

## 6️⃣ Cron Persistence Detection in Splunk (T1053)

**File:** `project6.png`  
✅ Splunk query:
```spl
index=* host=ubantu "CRON" "persistence-active"

---

## ✅ Cron Persistence Detection in Splunk (T1053)

**File:** `project6.png`

✅ Shows:
- Repeated root cron execution  
- Continuous persistence activity  

✅ This validates:
- Real SOC persistence detection logic  
- Reliable monitoring of scheduled task abuse  

---

## 7️⃣ Ransomware Encryption Detection in Splunk (T1486)

**File:** `project7.png`

✅ Splunk Query Used:
```spl
index=* host=ubantu ("openssl" OR ".locked" OR "README_RESTORE")
✅ Detects:

Cryptographic encryption behavior

Ransomware-related indicators

✅ Mapped to:

MITRE T1486 – Data Encrypted for Impact

8️⃣ Real-Time Alert Creation in Splunk
File: project8.png

✅ Shows live creation of the alert:

mathematica
Copy code
Suspicious Root Cron Persistence - T1053
✅ Alert Configuration:

Real-time trigger

Trigger condition: Results > 0

✅ Confirms:

Automated SOC alerting is active

Immediate detection of malicious persistence activity
