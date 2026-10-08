import json, sys

with open('eval/results/run-20261007-171701/results.json') as f:
    data = json.load(f)

results = data.get('results', [])
runnable = [r for r in results if r.get('status') == 'runnable']

if not runnable:
    print("No runnable cases yet.")
    sys.exit(0)

# Extract scores for calibration
calib_data = []
for r in runnable:
    expected = r.get('expected')
    if expected not in ('malicious', 'benign'): continue
    label = 1 if expected == 'malicious' else 0
    score = r.get('score', 0)
    calib_data.append({"logit": score, "label": label})

with open('eval/calib_data.jsonl', 'w') as f:
    for item in calib_data:
        f.write(json.dumps(item) + '\n')

# Stats
uncertain = [r for r in runnable if r.get('verdict') == 'uncertain']
correct = [r for r in runnable if r.get('correct')]
malicious_total = sum(1 for r in runnable if r.get('expected') == 'malicious')
misses = [r for r in runnable if r.get('expected') == 'malicious' and r.get('verdict') == 'benign']

accuracy = len(correct) / len(runnable) if runnable else 0
decisive_count = len(runnable) - len(uncertain)
decisive_accuracy = len([r for r in correct if r.get('verdict') != 'uncertain']) / decisive_count if decisive_count > 0 else 0
uncertain_rate = len(uncertain) / len(runnable) if runnable else 0
miss_rate = len(misses) / malicious_total if malicious_total else 0

print(f"Total runnable: {len(runnable)}")
print(f"Malicious Total: {malicious_total}")
print(f"Misses: {len(misses)}")
print(f"Correct: {len(correct)}")
print(f"Accuracy: {accuracy:.1%}")
print(f"Decisive Accuracy: {decisive_accuracy:.1%}")
print(f"Uncertain Rate: {uncertain_rate:.1%}")
print(f"Miss Rate: {miss_rate:.1%}")

# Did large_value_transfer catch anything?
caught = []
for r in runnable:
    if r.get('expected') == 'malicious' and r.get('verdict') != 'benign':
        features = r.get('features', [])
        if 'sim.large_value_transfer' in features:
            caught.append(r)

print(f"\nCaught {len(caught)} massive value attacks with new feature:")
for c in caught:
    print(f" - {c.get('tx_hash')} (Verdict: {c.get('verdict')}, Score: {c.get('score')})")

missing = []
for r in runnable:
    features = r.get('features', [])
    if 'sim.price_unavailable' in features:
        missing.append(r)
print(f"Cases with missing prices: {len(missing)}")
