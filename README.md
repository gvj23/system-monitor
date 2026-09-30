# 🖥️ System Monitor

A real-time system monitoring platform built with **Python, FastAPI, React, WebSockets, and SQLite**.

The platform collects system health metrics from monitored machines and displays them in a live dashboard with real-time updates.

---

## 🚀 Features

### System Monitoring
- CPU Usage
- RAM Usage
- Disk Usage
- System Uptime
- Hostname & OS Information

### Process Monitoring
- Top CPU-consuming processes
- Process status monitoring

### Network Monitoring
- Network I/O statistics
- Open Ports Detection
- Active Connections

### Security Monitoring
- Logged-in Users
- Sudo Command Tracking
- SSH Login History
- Failed SSH Attempts
- Installed Package Tracking

### Service Monitoring
- Failed Systemd Services
- Recent System Errors

### Real-Time Dashboard
- WebSocket-based updates
- Live charts
- Agent online/offline status
- Historical metrics

### Database Storage
- SQLite persistence
- Historical metric retention
- CPU/RAM trend history

---

# 🏗 Architecture

```text
┌──────────────────────┐
│     Agent Layer      │
│  (Python + psutil)   │
└──────────┬───────────┘
           │ POST /metrics
           ▼
┌──────────────────────┐
│    FastAPI Backend   │
│      WebSocket       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      SQLite DB       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   React Dashboard    │
│   Live Monitoring    │
└──────────────────────┘
```

---

# 📂 Project Structure

```text
system-monitor/
│
├── agent/
│   ├── agent.py
│   ├── metrics.py
│   ├── sender.py
│   ├── security.py
│   ├── network_scan.py
│   ├── report.py
│   ├── config.py
│   └── requirements.txt
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── monitor.db
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

# 🔄 Data Flow

```text
Agent
  │
  ├─ Collect Metrics
  │
  ├─ CPU
  ├─ RAM
  ├─ Disk
  ├─ Network
  ├─ Processes
  ├─ Security
  │
  ▼
FastAPI Backend
  │
  ├─ Store Latest Data
  ├─ Save History (SQLite)
  ├─ Broadcast WebSocket Events
  │
  ▼
React Dashboard
  │
  └─ Live Monitoring UI
```

---

# 📡 API Endpoints

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "agent_status": "online"
}
```

---

## Latest Metrics

```http
GET /metrics
```

---

## Historical Metrics

```http
GET /metrics/history
```

---

## Database History

```http
GET /metrics/db-history
```

---

## Submit Metrics

```http
POST /metrics
```

---

## Network Scan

```http
GET /network-scan
```

---

# 🔌 WebSocket

```text
ws://localhost:8000/ws
```

Example message:

```json
{
  "type": "metrics",
  "data": {
    "cpu": {
      "usage_percent": 24
    }
  }
}
```

---

# 🗄 Database

SQLite database:

```text
monitor.db
```

Table:

```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    hostname TEXT,
    cpu_percent REAL,
    ram_percent REAL,
    disk_percent REAL,
    full_data TEXT
);
```

---

# ⚙ Backend Setup

```bash
cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URL:

```text
http://localhost:8000
```

---

# ⚙ Agent Setup

```bash
cd agent

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python agent.py
```

---

# ⚙ Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

# 📊 Sample Metrics Payload

```json
{
  "timestamp": "2026-09-30 10:00:00",
  "system": {
    "hostname": "server01",
    "ip_address": "192.168.1.100"
  },
  "cpu": {
    "usage_percent": 15
  },
  "ram": {
    "usage_percent": 42
  },
  "disk": {
    "usage_percent": 60
  }
}
```

---

# 🛠 Technologies Used

### Backend
- Python
- FastAPI
- WebSocket
- SQLite
- Pydantic

### Agent
- Python
- psutil
- requests

### Frontend
- React
- Vite
- JavaScript

### Monitoring
- Systemd
- Journalctl
- SSH Audit
- Network Scanning

---

# 🔒 Security Features

- SSH Login Monitoring
- Failed SSH Detection
- Sudo Command Auditing
- Logged-In User Tracking
- Package Installation Tracking

---

# 📈 Future Enhancements

- PostgreSQL Support
- Multi-Agent Monitoring
- Alerting Engine
- Email Notifications
- Telegram Notifications
- Docker Deployment
- Kubernetes Support
- Role-Based Access Control (RBAC)
- Grafana Integration

---

# 👨‍💻 Author

**K Gunasekaran**

Software Engineer | Linux Administrator | DevOps Enthusiast

---

# 📄 License

MIT License
