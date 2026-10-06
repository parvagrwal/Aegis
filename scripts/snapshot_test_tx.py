import json
import os
from pathlib import Path

# Synthesized "real" looking transaction JSONs for testing
TXS = {
    "approve": {
        "hash": "0xapprove",
        "input": "0x095ea7b3000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff0000000000000000000000000000000000000000000000000de0b6b3a7640000",
        "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "type": "0x2",
        "authorizationList": []
    },
    "setApprovalForAll": {
        "hash": "0xsetApprovalForAll",
        "input": "0xa22cb465000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff0000000000000000000000000000000000000000000000000000000000000001",
        "to": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
        "type": "0x2"
    },
    "create": {
        "hash": "0xcreate",
        "input": "0x608060405234801561001057600080fd5b5060f58061001f6000396000f3fe",
        "to": None,
        "type": "0x2"
    },
    "type4": {
        "hash": "0xtype4",
        "input": "0x",
        "to": "0x1111111111111111111111111111111111111111",
        "type": "0x4",
        "authorizationList": [
            {
                "chainId": "0x1",
                "address": "0x2222222222222222222222222222222222222222",
                "nonce": "0x0",
                "v": "0x1b",
                "r": "0x1111111111111111111111111111111111111111111111111111111111111111",
                "s": "0x1111111111111111111111111111111111111111111111111111111111111111"
            }
        ]
    }
}

def main():
    target_dir = Path(__file__).parent.parent / "backend" / "tests" / "data"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for name, tx in TXS.items():
        with open(target_dir / f"{name}.json", "w") as f:
            json.dump(tx, f, indent=2)
    print(f"Snapshotted {len(TXS)} transactions to {target_dir}")

if __name__ == "__main__":
    main()
