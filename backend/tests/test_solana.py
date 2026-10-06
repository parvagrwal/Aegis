import pytest
from aegis.detect.solana_features import detect_solana_approve

def test_solana_devnet_spl_approve():
    # Mocking a watched wallet SPL approve event
    tx = {
        "type": "SPL_APPROVE",
        "delegate": "UNKNOWN_RANDOM_DELEGATE"
    }
    
    features = detect_solana_approve(tx)
    assert len(features) > 0
    assert features[0]["id"] == "sol.token_approve_unknown_delegate"
