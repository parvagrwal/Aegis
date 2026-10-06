import time
from aegis.intel.labels import get_label

def test_label_lookup_speed():
    # Warm up
    _ = get_label("0x123")
    
    start = time.perf_counter()
    ans = get_label("0x1111111111111111111111111111111111111111")
    end = time.perf_counter()
    
    elapsed_ms = (end - start) * 1000
    assert elapsed_ms < 1.0, f"Lookup took {elapsed_ms} ms, expected < 1 ms"
