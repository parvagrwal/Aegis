from typing import Any
import hashlib

class Memory:
    def __init__(self):
        self.clusters = {}
        self.fingerprints = {}
        
    def add_anchor(self, case_id: str, anchor_data: dict):
        pass
        
    def compute_similarity(self, fp1: str, fp2: str) -> float:
        # Simple jaccard or exact match for now
        return 1.0 if fp1 == fp2 else 0.0
        
    def get_cluster(self, address: str) -> str:
        return self.clusters.get(address, "unknown")
        
    def generate_fingerprint(self, tx_data: dict) -> str:
        # A fingerprint of the transaction's structure (e.g. methods and to address)
        raw = f"{tx_data.get('to', '')}:{tx_data.get('input', '0x')[:10]}"
        return hashlib.sha256(raw.encode()).hexdigest()
