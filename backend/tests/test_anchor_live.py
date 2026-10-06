import pytest
import os
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

@pytest.mark.live
def test_anchor_live():
    from aegis.attest.anchor_evm import anchor_records
    
    # Dummy data
    case_key = b"c" * 32
    version = 1
    record_hash = b"r" * 32
    verdict = 1
    conf = 5000
    
    tx_hash = anchor_records([case_key], [version], [record_hash], [verdict], [conf])
    assert tx_hash.startswith("0x")
    print(f"Anchored at: {tx_hash}")
    # We could poll for receipt but returning the hash means it broadcasted.
