import hashlib
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aegis.attest.record import canonical_serialize

def verify(record: dict, expected_hash: str) -> bool:
    b = canonical_serialize(record)
    h = hashlib.sha256(b).hexdigest()
    return h == expected_hash

if __name__ == "__main__":
    r = {"a": 1, "b": 2}
    expected = hashlib.sha256(canonical_serialize(r)).hexdigest()
    
    if verify(r, expected):
        print("PASS")
    else:
        print("FAIL")
        
    r["a"] = 2
    if verify(r, expected):
        print("PASS")
    else:
        print("FAIL")
