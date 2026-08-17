from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from models import MetricsPayload
import database as db

app = FastAPI(title="System Monitor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "System Monitor Backend is running 🚀", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "agent_status": db.get_agent_status()}

@app.post("/metrics")
async def receive_metrics(payload: MetricsPayload):
    data = payload.model_dump()
    db.update_metrics(data)
    await broadcast_to_clients(data)
    return {"status": "ok", "message": "Metrics received"}

@app.get("/metrics/history")
def get_history():
    return {"status": "ok", "history": db.get_cpu_history()}

@app.get("/metrics/db-history")
def get_db_history(limit: int = 100):
    return {"status": "ok", "history": db.get_db_history(limit)}

@app.get("/metrics")
def get_metrics():
    latest = db.get_latest()
    if latest is None:
        return {"status": "waiting", "message": "No data yet — agent not connected"}
    return {
        "status": "ok",
        "agent_status": db.get_agent_status(),
        "data": latest,
        "history": db.get_cpu_history()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    db.connected_clients.append(websocket)
    print(f"✅ Dashboard connected | Total clients: {len(db.connected_clients)}")
    try:
        latest = db.get_latest()
        if latest:
            await websocket.send_json({
                "type": "initial",
                "data": latest,
                "history": db.get_cpu_history()
            })
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        db.connected_clients.remove(websocket)
        print(f"❌ Dashboard disconnected | Remaining: {len(db.connected_clients)}")

async def broadcast_to_clients(data: dict):
    disconnected = []
    for client in db.connected_clients:
        try:
            await client.send_json({
                "type": "metrics",
                "data": data,
                "history": db.get_cpu_history(),
                "agent_status": db.get_agent_status()
            })
        except Exception:
            disconnected.append(client)
    for client in disconnected:
        db.connected_clients.remove(client)



@app.get("/network-scan")
def network_scan():
    """Trigger network scan — runs on demand not every 5s"""
    import sys
    sys.path.append("/root/system-monitor/agent")
    from network_scan import scan_network
    return scan_network()
