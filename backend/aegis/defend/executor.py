from aegis.defend.queue import DefendQueue

class Executor:
    def __init__(self, queue: DefendQueue):
        self.queue = queue
        
    def execute(self, action_id: str):
        item = self.queue.get(action_id)
        if not item:
            raise ValueError("Action not found")
            
        if item["status"] == "pending":
            raise PermissionError("Action not approved")
            
        if item["status"] != "approved":
            raise PermissionError(f"Action cannot be executed. Status: {item['status']}")
            
        item["status"] = "executed"
        return {"success": True}
