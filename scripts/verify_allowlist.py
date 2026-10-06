import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from aegis.intel.allowlist import is_allowed, is_mixer, is_delegate
from aegis.intel.labels import get_label

def main():
    print("Verifying allowlists and labels...")
    
    # Just a quick check to see if imports work and we can call the functions
    start = time.perf_counter()
    ans = is_allowed("0x0000000000000000000000000000000000000000")
    end = time.perf_counter()
    
    print(f"Allowlist check took {(end-start)*1000:.4f} ms (Result: {ans})")
    print("Verification complete.")

if __name__ == "__main__":
    main()
