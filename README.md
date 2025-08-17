# Process Monitoring System (Agent + Django Backend + Frontend)

A complete, minimal implementation matching the assignment. Tested for local development.

## Components
- **backend/** – Django + DRF API, SQLite DB, API key auth (header: `X-API-Key`)
- **agent/** – Python script using `psutil` to collect processes and POST to backend
- **frontend/** – Static HTML/JS tree viewer that fetches latest snapshot

## Quickstart

### 1) Backend (Django)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit BACKEND_API_KEY if desired
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
APIs:
- POST `http://127.0.0.1:8000/api/ingest/` (header `X-API-Key: mysecretkey`)
- GET  `http://127.0.0.1:8000/api/latest?hostname=YOUR-HOSTNAME`
- GET  `http://127.0.0.1:8000/api/hosts/`

### 2) Agent
```bash
cd agent
pip install -r requirements.txt
python agent.py --endpoint http://127.0.0.1:8000/api/ingest --api-key mysecretkey
```
Optional: repeat sending every N seconds
```bash
python agent.py --endpoint http://127.0.0.1:8000/api/ingest --api-key mysecretkey --interval 5
```

**Build EXE (Windows):**
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole agent.py
# Output: dist/agent.exe (double-click to run; configure ENDPOINT and API_KEY env vars)
```

### 3) Frontend
Open `frontend/index.html` in your browser, set **Backend Base URL** and **Hostname**, click **Refresh**.
- Auto-refresh every 5s supported via checkbox.

## Notes
- The frontend builds the tree in-browser from a flat process list (pid/ppid).
- API key is set in backend `.env` as `BACKEND_API_KEY`. The agent sends it in `X-API-Key` header.
- SQLite DB file is at `backend/server/db.sqlite3` by default.

## Bonus ideas
- WebSockets (Django Channels) for real-time updates.
- History view: store & query older snapshots per host.
- Filtering/search on process name / pid.
- Charts of top CPU/memory processes.
