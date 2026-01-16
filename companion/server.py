import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3
import os
import logging
from typing import List, Optional
from pydantic import BaseModel
import datetime

# Configuration
app = FastAPI(title="Antigravity Companion")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ag-companion")

# Database Path - Default to a mock if not found
DB_PATH = os.getenv("AG_STATE_DB", "/data/state/state.vscdb")
USE_MOCK = not os.path.exists(DB_PATH)

# Models
class PendingItem(BaseModel):
    id: str
    title: str
    description: str
    timestamp: str
    status: str  # "pending", "approved", "rejected"

# Mock Data Store
mock_items = [
    PendingItem(id="1", title="Approve Plan", description="Implementation plan for Docker", timestamp="2026-01-16 10:00", status="pending"),
    PendingItem(id="2", title="Run Command", description="sudo apt-get install tailscale", timestamp="2026-01-16 10:05", status="pending"),
]

@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "mode": "mock" if USE_MOCK else "live",
        "db_path": DB_PATH,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/inbox", response_model=List[PendingItem])
async def get_inbox():
    if USE_MOCK:
        return [i for i in mock_items if i.status == "pending"]
    
    # Real DB Implementation (Placeholder)
    # conn = sqlite3.connect(DB_PATH)
    # ... logic to query agent request table ...
    return []

@app.post("/api/approve/{item_id}")
async def approve_item(item_id: str):
    logger.info(f"Approving item {item_id}")
    if USE_MOCK:
        for item in mock_items:
            if item.id == item_id:
                item.status = "approved"
                return {"status": "success", "message": "Item approved"}
        raise HTTPException(status_code=404, detail="Item not found")

    # Real DB Implementation
    # ... logic to write approval back to state ...
    return {"status": "error", "message": "Write-back not implemented for real DB yet"}

# Serve Frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    logger.info("Starting server...")
    if USE_MOCK:
        logger.warning(f"⚠️  Database not found at {DB_PATH}. Using MOCK data.")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
