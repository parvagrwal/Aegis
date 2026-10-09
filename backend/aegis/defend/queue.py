import sqlite3
import json
import time
import secrets
from pathlib import Path

class DefendQueue:
    def __init__(self, db_path="queue.db"):
        self.db_path = Path(__file__).parent.parent.parent.parent / db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS defend_queue (
                    id TEXT PRIMARY KEY,
                    action TEXT,
                    status TEXT,
                    created_at REAL,
                    expires_at REAL,
                    attempts INTEGER,
                    code TEXT,
                    tx_hash TEXT
                )
            """)
            
    def add(self, action_id: str, action: dict, expires_in_ms: int = 600000):
        code = secrets.token_hex(3)
        now = time.time()
        expires = now + expires_in_ms / 1000.0
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO defend_queue (id, action, status, created_at, expires_at, attempts, code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (action_id, json.dumps(action), "pending", now, expires, 0, code))
            
    def get(self, action_id: str) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM defend_queue WHERE id = ?", (action_id,)).fetchone()
            if not row:
                return None
            return {
                "action": json.loads(row["action"]),
                "status": row["status"],
                "expires_at": row["expires_at"],
                "attempts": row["attempts"],
                "code": row["code"],
                "tx_hash": row["tx_hash"]
            }
            
    def approve(self, action_id: str, code: str) -> bool:
        item = self.get(action_id)
        if not item or item["status"] != "pending":
            return False
            
        with sqlite3.connect(self.db_path) as conn:
            if time.time() > item["expires_at"]:
                conn.execute("UPDATE defend_queue SET status = 'expired' WHERE id = ?", (action_id,))
                return False
                
            if item["code"] != code:
                attempts = item["attempts"] + 1
                status = "rejected" if attempts >= 3 else "pending"
                conn.execute("UPDATE defend_queue SET attempts = ?, status = ? WHERE id = ?", (attempts, status, action_id))
                return False
                
            conn.execute("UPDATE defend_queue SET status = 'approved' WHERE id = ?", (action_id,))
            return True
            
    def set_status(self, action_id: str, status: str, tx_hash: str = None):
        with sqlite3.connect(self.db_path) as conn:
            if tx_hash:
                conn.execute("UPDATE defend_queue SET status = ?, tx_hash = ? WHERE id = ?", (status, tx_hash, action_id))
            else:
                conn.execute("UPDATE defend_queue SET status = ? WHERE id = ?", (status, action_id))
