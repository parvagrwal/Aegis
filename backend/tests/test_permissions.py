import pytest
from aegis.agent.permissions import check_permission
from aegis.agent.tools import revoke_approval, get_tools_for_role, ToolError

def test_narrator_cannot_call_tools():
    # Narrator has no tools
    tools = get_tools_for_role("narrator")
    assert len(tools) == 0
    
    # Check permissions explicitly
    assert check_permission("narrator", "any_action") is False
    
    with pytest.raises(ToolError):
        revoke_approval("narrator", 11155111, "0xtoken", "0xspender")

def test_executor_rejects_chain_1():
    # Executor can do it on Sepolia (11155111)
    assert check_permission("executor", "revoke_approval", 11155111) is True
    
    # Executor cannot do it on Mainnet (1)
    assert check_permission("executor", "revoke_approval", 1) is False
    
    with pytest.raises(ToolError):
        revoke_approval("executor", 1, "0xtoken", "0xspender")
