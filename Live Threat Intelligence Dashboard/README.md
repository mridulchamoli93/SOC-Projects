# ✅ **Thanatos – Live Threat Intelligence Dashboard**

*A real-time cyber-threat OSINT dashboard with 3D globe visualizations, IOC tracking, alert feed, automated log scanning & AbuseIPDB enrichment.*

Thanatos is a **fully interactive, cinematic threat-intelligence SOC dashboard** designed for security analysts, students, and researchers.
It features a **3D attack-globe**, **live alert feed**, **IOC database**, **auto-scanning engine**, and **IP lookup with AbuseIPDB integration** — all wrapped in a highly polished cyberpunk UI.

<div align="center">

🔥 **Interactive Dashboard** • 🌍 **3D Attack Globe** • 🚨 **Live Alerts**
🕵️ **IOC Intelligence** • 💾 **SQLite Backend** • ⚡ **Real-time Updates**

</div>

---

## 🌐 **Live UI Preview**
<img width="1903" height="877" alt="Screenshot 2025-12-03 141328" src="https://github.com/user-attachments/assets/c34b2a92-77cd-45f3-86cd-2777e8885d3c" />

---

# 🚀 Features

### ✅ **Real-Time Threat Dashboard**

* Animated **3D Earth** showing malicious IP arcs
* Global threat visualization using **three.js + three-globe**
* Dynamic stats (IOCs, alerts, high-risk indicators)

### 🚨 **Live Alert Feed**

* Auto-updating alert stream
* New alerts appear instantly (detected via diffing)
* Smooth GSAP animations

### 🕵️ **IOC Database**

* Stores malicious IPs, confidence scores & countries
* Sorted, filterable table with bulk actions
* CSV export (single or multi-select)

### 🔍 **IP Intelligence Lookup**

* “Search IP” (Ctrl+K) → instant lookup
* Checks:

  * Local DB
  * Recent alerts
  * Optional **AbuseIPDB live lookup**
* Drawer panel with:

  * Confidence score
  * Country & metadata
  * Recent alert history
  * Copy-to-clipboard
  * Globe zoom-to-IP

### ⚙️ **Automated Log Scanner**

* Background thread scans logs for known IOCs
* Matched entries automatically added to Alerts
* Batch email log (safe local write)
* Automatic demo data generation for first run

### 🧬 **Backend Highlights**

* Clean Flask app with modular structure
* Fully optimized threat processor
* Auto DB + directory creation
* SSE/WebSocket-ready architecture
* Portable SQLite-based persistence

---

# 🏛️ Project Structure

```
Live Threat Intelligence Dashboard/
│ app.py                          ← Flask entrypoint :contentReference[oaicite:0]{index=0}
│ dashboard_opt.py                ← Dashboard data provider :contentReference[oaicite:1]{index=1}
│ threat_processor_opt.py         ← Core intelligence engine :contentReference[oaicite:2]{index=2}
│ scan_once_opt.py                ← One-shot scan CLI :contentReference[oaicite:3]{index=3}
│
├── templates/
│   └── dashboard.html            ← Full UI dashboard :contentReference[oaicite:4]{index=4}
│
├── static/
│   └── style.css                 ← Full neon+3D UI theme :contentReference[oaicite:5]{index=5}
│
├── db/
│   └── threat_intel.db           ← Auto-created SQLite database
│
└── logs/
    └── access.log                ← Auto-generated log source
```

---

# 🛠️ Installation

### 1️⃣ Clone the repo

```bash
git clone https://github.com/mridulchamoli93/SOC-Projects/edit/main/Live%20Threat%20Intelligence%20Dashboard
cd Live Threat Intelligence Dashboard
```

### 2️⃣ Install dependencies

```bash
pip install flask requests python-dotenv
```

Optional (for AbuseIPDB & .env support):

```bash
pip install requests python-dotenv
```

### 3️⃣ Create folder structure (if missing)

```
db/
logs/
static/
templates/
```

### 4️⃣ Run the dashboard

```bash
python app.py
```

UI opens at:
👉 **[http://localhost:5000/](http://localhost:5000/)**

---

# 🔧 Environment Variables

Create a `.env` file:

```
ABUSEIPDB_KEY=your_api_key_here
TP_DB_FILE=db/threat_intel.db
```

If `ABUSEIPDB_KEY` is not set:

* Local DB is used first
* A small demo dataset is returned for specific IPs

---

# 📡 REST API Endpoints

### **GET /api/data**

Get latest IOCs + Alerts (used by polling & charts)

```json
{
  "iocs": [...],
  "alerts": [...]
}
```

### **POST /run_now**

Triggers background log scan.

```json
{"status": "scan started"}
```

### **POST /api/query_ip**

Lookup IP across DB + AbuseIPDB.

#### Request:

```json
{"ip": "185.191.171.12"}
```

### Response:

```json
{
  "found": true,
  "ioc": {
    "ip_address": "185.191.171.12",
    "abuse_confidence": 90,
    "country_code": "GB",
    "source": "demo"
  },
  "alerts": [...]
}
```

---

# 🧩 How It Works (Architecture)

### **1. Dashboard loads**

* Injects initial IOC + Alert data from Flask
* Initializes:

  * 3 charts (timeline, top IOC, distribution)
  * 3D globe
  * Live feed
  * Keyboard shortcuts
  * Boot animation

### **2. Background Polling Every 3s**

* `/api/data` returns new IOCs/alerts
* New alerts animate into feed
* Table + charts + globe update live

### **3. On Run Scan**

* `/run_now` starts thread → scans `logs/access.log`
* Matched entries inserted into DB
* Alerts appear in real-time

### **4. IP Lookup**

* UI → `/api/query_ip` → DB
* If missing & API key exists → AbuseIPDB
* Response shows in inspector panel

---

# 🎨 UI & UX Features

* Neon cyberpunk theme
* 3D rotating earth with animated arcs
* GSAP-powered transitions
* Cinematic boot sequence
* Real-time threat ticker (alerts feed)
* Accessible keyboard shortcuts
* Smooth hover interactions
* Responsive on all screens

---

# 🧪 Development Modes

### Generate Demo IOC + Logs

Auto-handled by:

```python
tp.ensure_demo_data()
```

📌 Ensures first-run experience is never empty.

---

# 🛡 Security Notes

Thanatos is intended **only for research & educational use**.
It does **not**:

* Perform offensive actions
* Deploy real malware
* Scan networks without authorization

All lookups & logs are **local to your machine** unless using AbuseIPDB.

---

# 🤝 Contributing

Pull requests welcome!
Open issues for bugs, enhancements, or feature requests.

Roadmap items include:

* WebSocket push updates
* MITRE mapping
* Full SIEM connectors
* Role-based access control
* Threat scoring AI assistant

---

# 📜 License

MIT License.
Free to use & modify for personal or commercial projects.

---

# 👤 Author

**Mridul Chamoli**
Cybersecurity Developer / SOC Automation Enthusiast
📧 [mridulchamoli93@gmail.com](mailto:mridulchamoli93@gmail.com)

---
