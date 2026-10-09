import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from aegis.attest.verify import verify_attestation
import json

async def main():
    if len(sys.argv) < 3:
        print("Usage: python verify_attestation.py <tx_hash> <local_result.json>")
        sys.exit(1)
        
    tx_hash = sys.argv[1]
    with open(sys.argv[2], 'r') as f:
        local_result = json.load(f)
        
    res = verify_attestation(tx_hash, local_result)
    if res.get("verified"):
        print("[+] VERIFIED")
        print(f"Local hash:    {res['local_hash']}")
        print(f"On-chain hash: {res['on_chain_hash']}")
    else:
        print("[-] UNVERIFIED")
        print(f"Error: {res.get('error', 'Hash mismatch')}")
        if res.get("local_hash"):
            print(f"Local hash:    {res['local_hash']}")
        if res.get("on_chain_hash"):
            print(f"On-chain hash: {res['on_chain_hash']}")

if __name__ == '__main__':
    asyncio.run(main())
