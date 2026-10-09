from aegis.defend.queue import DefendQueue
from aegis.agent.tools import revoke_approval

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
            
        # Agentic Action Execution
        action = item.get("action", {})
        if action.get("type") == "REVOKE_APPROVAL":
            spender = action.get("spender")
            token = action.get("token")
            chain_id = action.get("chain_id", 1)
            if spender and token:
                revoke_approval("defender", chain_id, token, spender)
                
        item["status"] = "executed"
        return {"success": True}