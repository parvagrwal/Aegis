import json
from pathlib import Path
from typing import Optional
import time

class LabelDB:
    def __init__(self):
        self.labels: dict[str, set[str]] = {}
        self.source_map: dict[str, str] = {}
        self._load()

    def _load(self):
        base_dir = Path(__file__).parent / "data"
        if not base_dir.exists():
            return
            
        for p in base_dir.glob("*.json"):
            try:
                with open(p, "r") as f:
                    data = json.load(f)
                    source_name = p.stem
                    
                    if isinstance(data, list):
                        for addr in data:
                            self._add(addr, "malicious", source_name)
                    elif isinstance(data, dict):
                        for addr, info in data.items():
                            label = info.get("label", "malicious") if isinstance(info, dict) else "malicious"
                            self._add(addr, label, source_name)
            except Exception:
                pass

    def _add(self, addr: str, label: str, source: str):
        addr_lower = addr.lower()
        if addr_lower not in self.labels:
            self.labels[addr_lower] = set()
        self.labels[addr_lower].add(label)
        self.source_map[addr_lower] = source

    def lookup(self, address: str) -> Optional[dict]:
        addr_lower = address.lower()
        if addr_lower in self.labels:
            return {
                "address": address,
                "labels": list(self.labels[addr_lower]),
                "source": self.source_map.get(addr_lower, "unknown")
            }
        return None

# Singleton
db = LabelDB()

def get_label(address: str) -> Optional[dict]:
    return db.lookup(address)
