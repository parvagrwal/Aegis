import json
from pathlib import Path
from typing import Optional

class AllowlistDB:
    def __init__(self):
        self.allowed: set[str] = set()
        self.mixers: set[str] = set()
        self.delegates: set[str] = set()
        self._load()

    def _load(self):
        base_dir = Path(__file__).parent / "data"
        
        # Load mainnet and sepolia allowlist
        for name in ["allowlist.mainnet.json", "allowlist.sepolia.json"]:
            p = base_dir / name
            if p.exists():
                try:
                    with open(p, "r") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for addr in data:
                                self.allowed.add(addr.lower())
                except Exception:
                    pass
                    
        # Load known delegates
        p = base_dir / "known_good_delegates.json"
        if p.exists():
            try:
                with open(p, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for addr in data:
                            self.delegates.add(addr.lower())
            except Exception:
                pass
                
        # Load mixers
        p = base_dir / "mixers.json"
        if p.exists():
            try:
                with open(p, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for addr in data:
                            self.mixers.add(addr.lower())
            except Exception:
                pass

    def is_allowed(self, address: str) -> bool:
        return address.lower() in self.allowed
        
    def is_mixer(self, address: str) -> bool:
        return address.lower() in self.mixers
        
    def is_delegate(self, address: str) -> bool:
        return address.lower() in self.delegates

# Singleton
db = AllowlistDB()

def is_allowed(address: str) -> bool:
    return db.is_allowed(address)
    
def is_mixer(address: str) -> bool:
    return db.is_mixer(address)
    
def is_delegate(address: str) -> bool:
    return db.is_delegate(address)
