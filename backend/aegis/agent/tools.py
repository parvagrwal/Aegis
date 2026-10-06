from aegis.agent.permissions import check_permission

class ToolError(Exception):
    pass

def revoke_approval(role: str, chain_id: int, token: str, spender: str):
    if not check_permission(role, "revoke_approval", chain_id):
        raise ToolError("Permission denied")
    return {"status": "queued"}
    
def get_tools_for_role(role: str):
    if role == "narrator":
        return []
    return [revoke_approval]
