import time

class DefendQueue:
    def __init__(self):
        self.queue = {}
        
    def add(self, action_id: str, action: dict, expires_in_ms: int = 600000):
        self.queue[action_id] = {
            "action": action,
            "expires_at": time.time() + expires_in_ms / 1000.0,
            "status": "pending",
            "attempts": 0,
            "code": "1234" # Dummy 2FA code for testing
        }
        
    def get(self, action_id: str) -> dict:
        return self.queue.get(action_id)
        
    def approve(self, action_id: str, code: str) -> bool:
        item = self.queue.get(action_id)
        if not item or item["status"] != "pending":
            return False
            
        if time.time() > item["expires_at"]:
            item["status"] = "expired"
            return False
            
        if item["code"] != code:
            item["attempts"] += 1
            if item["attempts"] >= 3:
                item["status"] = "rejected"
            return False
            
        item["status"] = "approved"
        return True
