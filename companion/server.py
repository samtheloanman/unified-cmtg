import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import sqlite3
import os
import json
import logging
from typing import List, Optional
from pydantic import BaseModel
import datetime

# Configuration
app = FastAPI(title="Antigravity Companion")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ag-companion")

# Paths
BRAIN_DIR = Path(os.getenv("AG_BRAIN_DIR", os.path.expanduser("~/.gemini/antigravity/brain")))
CONVERSATIONS_DIR = Path(os.getenv("AG_CONVERSATIONS_DIR", os.path.expanduser("~/.gemini/antigravity/conversations")))
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
        "brain_dir": str(BRAIN_DIR),
        "db_path": DB_PATH,
        "timestamp": datetime.datetime.now().isoformat()
    }

# Conversation Model
class Conversation(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    updated_at: Optional[str] = None
    agent: str = "antigravity"
    has_task: bool = False

def scan_conversations() -> List[Conversation]:
    """Scan brain directories for active conversations and extract metadata."""
    conversations = []
    
    if not BRAIN_DIR.exists():
        logger.warning(f"Brain directory not found: {BRAIN_DIR}")
        return conversations
    
    for conv_dir in BRAIN_DIR.iterdir():
        if not conv_dir.is_dir():
            continue
        
        conv_id = conv_dir.name
        title = f"Conversation {conv_id[:8]}"
        summary = None
        updated_at = None
        has_task = False
        
        # Try to get title from task.md
        task_file = conv_dir / "task.md"
        if task_file.exists():
            has_task = True
            try:
                with open(task_file, 'r') as f:
                    first_line = f.readline().strip()
                    # Remove markdown header prefix
                    if first_line.startswith('#'):
                        title = first_line.lstrip('#').strip()
            except Exception as e:
                logger.warning(f"Error reading task.md: {e}")
        
        # Try to get metadata
        meta_file = conv_dir / "task.md.metadata.json"
        if meta_file.exists():
            try:
                with open(meta_file, 'r') as f:
                    meta = json.load(f)
                    summary = meta.get("summary", "")
                    updated_at = meta.get("updatedAt", "")
            except Exception as e:
                logger.warning(f"Error reading metadata: {e}")
        
        # Fallback to file modification time
        if not updated_at:
            try:
                pb_file = CONVERSATIONS_DIR / f"{conv_id}.pb"
                if pb_file.exists():
                    mtime = pb_file.stat().st_mtime
                    updated_at = datetime.datetime.fromtimestamp(mtime).isoformat()
            except Exception:
                pass
        
        conversations.append(Conversation(
            id=conv_id,
            title=title,
            summary=summary,
            updated_at=updated_at,
            agent="antigravity",
            has_task=has_task
        ))
    
    # Sort by updated_at descending (most recent first)
    conversations.sort(key=lambda c: c.updated_at or "", reverse=True)
    return conversations

@app.get("/api/conversations", response_model=List[Conversation])
async def get_conversations():
    """Get all active conversations from the Antigravity IDE."""
    return scan_conversations()

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
