import json
import os
from pathlib import Path
from cachetools import TTLCache
import time

cache = TTLCache(maxsize=1, ttl=600) # 10 min cache

def load_static_prices() -> dict:
    if "prices" in cache:
        return cache["prices"]
        
    p = Path(__file__).parent.parent.parent / "config" / "prices.static.json"
    if not p.exists():
        return {}
        
    try:
        with open(p, "r") as f:
            data = json.load(f)
            cache["prices"] = data.get("prices", {})
            return cache["prices"]
    except Exception:
        return {}

def get_price(token_address: str) -> float:
    prices = load_static_prices()
    return prices.get(token_address.lower(), 0.0)
