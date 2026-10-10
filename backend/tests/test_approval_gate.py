import pytest
import time
import os
from aegis.defend.queue import DefendQueue
from aegis.defend.executor import Executor

def test_approval_gate():
    if os.path.exists("queue.db"):
        os.remove("queue.db")
    q = DefendQueue()
    e = Executor(q)
    
    # 1. No approval -> no execution
    q.add("act1", {})
    with pytest.raises(PermissionError, match="Action not approved|Action cannot be executed"):
        e.execute("act1")
        
    # 2. Wrong code x3 -> rejected
    q.add("act2", {})
    assert q.approve("act2", "0000") is False
    assert q.approve("act2", "0000") is False
    assert q.approve("act2", "0000") is False
    assert q.get("act2")["status"] == "rejected"
    with pytest.raises(PermissionError, match="Action not approved|Action cannot be executed"):
        e.execute("act2")
        
    # 3. Expiry
    q.add("act3", {}, expires_in_ms=-100) # already expired
    assert q.approve("act3", "1234") is False
    assert q.get("act3")["status"] == "expired"
    
    # 4. Success path
    q.add("act4", {})
    code = q.get("act4")["code"]
    assert q.approve("act4", code) is True
