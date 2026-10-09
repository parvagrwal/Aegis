import json

with open("eval/results/run-final/results.json") as f:
    results = json.load(f).get("results", [])

with open("eval/cases.json") as f:
    cases = json.load(f)

# Create a mapping of tx_hash to case details
case_map = {}
for i, c in enumerate(cases):
    tx = c.get("tx_hash")
    if tx:
        case_map[tx] = {
            "index": i,
            "incident": c.get("incident", "Unknown"),
            "attack_type": c.get("attack_type", c.get("type", "Unknown"))
        }

original_misses = []
fresh_misses = []

for r in results:
    if r.get("expected") == "malicious" and r.get("verdict") == "benign":
        tx = r.get("tx_hash")
        cinfo = case_map.get(tx, {"index": -1, "incident": "Unknown", "attack_type": "Unknown"})
        
        info_str = f"- Hash: {tx}\n  Incident: {cinfo['incident']}\n  Type: {cinfo['attack_type']}\n  Score: {r.get('score')}\n  Features: {r.get('features', [])}\n"
        
        # 334 was the original size.
        if cinfo["index"] < 334:
            original_misses.append(info_str)
        else:
            fresh_misses.append(info_str)

print("### (a) The remaining misses from the original 334 cases:\n")
for m in original_misses:
    print(m)

print("### (b) New misses from the 40 fresh cases:\n")
for m in fresh_misses:
    print(m)
