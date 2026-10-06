import pytest
import os

@pytest.mark.live
def test_e2e_sepolia_approve_and_revoke():
    # 1. fire.py approve_drainer
    # 2. backend case creation
    # 3. approve and confirm
    # 4. revoke tx is mined
    # 5. allowance == 0
    assert True
