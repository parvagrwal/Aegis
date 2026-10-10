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
            
        tx_hash = None
        # Agentic Action Execution
        action = item.get("action", {})
        if action.get("type") == "REVOKE_APPROVAL":
            spender = action.get("spender")
            token = action.get("token")
            chain_id = action.get("chain_id", 1)
            if spender and token:
                res = revoke_approval("executor", chain_id, token, spender)
                tx_hash = res.get("tx_hash")
                
        self.queue.set_status(action_id, "executed", tx_hash)
        return {"success": True, "tx_hash": tx_hash}