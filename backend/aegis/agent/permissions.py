from typing import Optional

def check_permission(role: str, action: str, chain_id: Optional[int] = None) -> bool:
    if role == "narrator":
        return False
        
    if role == "executor" and chain_id == 1:
        # Executor is strictly prohibited from executing state-changing txs on Mainnet
        return False
        
    return True
