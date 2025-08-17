# 🖥️ Process Monitoring System (Agent + Django Backend + Frontend)

This project is a complete **Process Monitoring System** that collects process information from a Windows machine (via an Agent) and displays it in a web-based UI powered by Django.

---

## 📌 Features

- **Agent (EXE/Python)**
  - Collects running processes and subprocesses
  - Captures process name, PID, PPID, CPU %, Memory (MB), Hostname
  - Sends data to backend via REST API
  - Configurable backend URL & API key (via `config.ini`)
  - Can be compiled to **standalone EXE** using PyInstaller

- **Backend (Django + DRF)**
  - REST API for ingestion and retrieval
  - SQLite database for storage
  - Authentication using **API key**
  - Endpoints for process ingestion, fetching latest snapshot, and listing hosts/snapshots

- **Frontend (HTML + JS + CSS)**
  - Run Index.html through Live server
  - Interactive **tree view** of processes
  - Expandable/collapsible subprocesses
  - Displays **hostname** and **latest timestamp**
  - Clean, responsive UI

---

## 📂 Project Structure

```
process-monitor/
│── backend/               # Django backend (API + UI)
│   ├── manage.py
│   ├── process_monitor/   # Django project
│   └── monitor/           # App (models, views, serializers, templates, static)
│
│── agent/                 # Process monitoring agent
│   ├── agent.py
│   ├── config.ini
│ 
│── Frontend 
    ├── index.html
│   ├── app.js
│   └── style.css
│── requirements.txt       # Python dependencies
│── README.md              # Documentation (this file)
```

---

## ⚙️ Setup & Installation

### 1. Clone project & create virtual environment
```bash
git clone <repo-url>
cd process-monitor
python -m venv .venv
# Activate venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API key
Choose a key (e.g., `mysecretkey`). Set it as an environment variable:
```bash
# Linux/Mac
export MONITOR_API_KEY=mysecretkey

# Windows (PowerShell)
$env:MONITOR_API_KEY="mysecretkey"
```

### 4. Run the backend server
```bash
cd backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🚀 Running the Agent

1. Open `agent/config.ini` and set:
   ```ini
   [agent]
   backend_url = http://127.0.0.1:8000/api/ingest/
   api_key = mysecretkey
   interval_seconds = 30
   ```

2. Run the agent:
   ```bash
   cd agent
   python agent.py
   ```

3. (Optional) Build standalone EXE:
   ```bash
   pip install pyinstaller
   pyinstaller --onefile agent.py
   # EXE will appear under dist/agent.exe
   ```

---

## 🔌 API Endpoints

- **POST** `/api/ingest/`  
  Ingest process snapshot (requires `X-API-Key` header).

- **GET** `/api/hosts/`  
  List all hostnames.

- **GET** `/api/processes/latest/?hostname=<host>`  
  Fetch latest snapshot for a hostname.

- **GET** `/api/snapshots/?hostname=<host>`  
  List all snapshot timestamps for a host.

---


## 📖 Assumptions
- Only a single API key is used (environment variable `MONITOR_API_KEY`).
- Agent runs on Windows, but can also run on Linux/Mac for testing.
- Database is SQLite for simplicity, but can be swapped with PostgreSQL/MySQL.

---

## ✅ Evaluation Criteria
- **Functionality:** Agent → Backend → Frontend integration works
- **Code Quality:** Modular, documented, error-handled
- **User Experience:** Clean UI, intuitive process hierarchy
- **Deployment:** Easy to run (minimal setup)

---

👨‍💻 Built with **Python, Django, DRF, psutil, HTML/JS**
