import json

def canonical_serialize(data: dict) -> bytes:
    # Recursively check for floats
    def check_floats(obj):
        if isinstance(obj, float):
            raise TypeError("Floats are not allowed in canonical serialization")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                check_floats(v)
        elif isinstance(obj, list):
            for v in obj:
                check_floats(v)

    check_floats(data)
    
    # Sort keys for deterministic output
    return json.dumps(data, separators=(',', ':'), sort_keys=True).encode('utf-8')
