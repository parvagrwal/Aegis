#!/usr/bin/env python3
"""Fit temperature scaling for the AEGIS policy engine.

Reads labeled (logit, label) pairs, fits a temperature T that minimizes
negative log-likelihood on a train split, evaluates it on a holdout split,
and writes the result into backend/config/policy.v1.json's calibration block.

Model:  p(malicious) = sigmoid(score_milli / 1000 / T)
The engine divides the raw additive score by T before applying risk bands.

Refuses to fit with fewer than --min-samples samples (default 20): a
temperature fitted on a handful of points is noise, not calibration.

Pure stdlib. Usage:
    python backend/aegis/policy/calibration.py --data eval/calibration_pairs.jsonl
    python backend/aegis/policy/calibration.py --data eval/calibration_pairs.jsonl \
        --min-samples 50 --holdout 0.3 --seed 7

Input format (JSONL, one object per line):
    {"logit": -500, "label": 0}
    {"logit": 6200, "label": 1}

`logit` is the engine's raw score in milli-logit units (the "score" field in
harness results). `label` is 1 for malicious, 0 for benign.
"""

import argparse
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path


def sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def nll(pairs, temperature: float) -> float:
    """Mean negative log-likelihood of the pairs at temperature T."""
    total = 0.0
    for logit, label in pairs:
        p = sigmoid(logit / 1000.0 / temperature)
        p = min(max(p, 1e-12), 1.0 - 1e-12)
        total += -(label * math.log(p) + (1 - label) * math.log(1 - p))
    return total / len(pairs)


def golden_section_minimize(f, lo: float, hi: float, tol: float = 1e-6):
    """Minimize unimodal f on [lo, hi]. Returns (x_min, f(x_min))."""
    inv_phi = (math.sqrt(5.0) - 1.0) / 2.0
    inv_phi_sq = (3.0 - math.sqrt(5.0)) / 2.0
    a, b = lo, hi
    h = b - a
    if h <= tol:
        return (a + b) / 2.0, f((a + b) / 2.0)
    n = int(math.ceil(math.log(tol / h) / math.log(inv_phi)))
    c = a + inv_phi_sq * h
    d = a + inv_phi * h
    fc, fd = f(c), f(d)
    for _ in range(n):
        if fc < fd:
            b, d, fd = d, c, fc
            h = inv_phi * h
            c = a + inv_phi_sq * h
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            h = inv_phi * h
            d = a + inv_phi * h
            fd = f(d)
    x = (a + b) / 2.0
    return x, f(x)


def fit_temperature(train_pairs):
    """Grid search + golden-section refinement of train NLL over T."""
    grid = [0.05 * (400.0 ** (i / 79.0)) for i in range(80)]  # 0.05 .. 20 log-spaced
    best_t = min(grid, key=lambda t: nll(train_pairs, t))
    lo = max(0.05, best_t / 3.0)
    hi = min(20.0, best_t * 3.0)
    t_opt, _ = golden_section_minimize(lambda t: nll(train_pairs, t), lo, hi)
    return t_opt


def load_pairs(path: Path):
    pairs = []
    with open(path, "r") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            logit = float(obj["logit"])
            label = int(obj["label"])
            if label not in (0, 1):
                raise ValueError(f"{path}:{lineno}: label must be 0 or 1, got {label!r}")
            pairs.append((logit, label))
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser(description="Fit temperature scaling for the policy engine.")
    ap.add_argument("--data", required=True, help="JSONL file of {logit, label} pairs")
    ap.add_argument("--policy", default=None, help="policy JSON to update (default: backend/config/policy.v1.json)")
    ap.add_argument("--min-samples", type=int, default=20, help="refuse to fit below this many samples")
    ap.add_argument("--holdout", type=float, default=0.3, help="fraction held out for evaluation")
    ap.add_argument("--seed", type=int, default=7, help="shuffle seed for the train/holdout split")
    args = ap.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"ERROR: data file not found: {data_path}", file=sys.stderr)
        return 2

    pairs = load_pairs(data_path)
    if len(pairs) < args.min_samples:
        print(
            f"REFUSING TO FIT: only {len(pairs)} labeled samples, need at least "
            f"{args.min_samples}. A temperature fitted on this little data is noise, "
            f"not calibration. Fire more redteam scenarios (or label more historical "
            f"transactions), rebuild the pairs file, and re-run.",
            file=sys.stderr,
        )
        return 3

    rng = random.Random(args.seed)
    idx = list(range(len(pairs)))
    rng.shuffle(idx)
    n_hold = max(1, int(round(len(pairs) * args.holdout)))
    hold_idx = set(idx[:n_hold])
    train = [p for i, p in enumerate(pairs) if i not in hold_idx]
    hold = [p for i, p in enumerate(pairs) if i in hold_idx]

    temperature = fit_temperature(train)
    train_nll = nll(train, temperature)
    hold_nll = nll(hold, temperature)
    # Baseline for comparison: uncalibrated (T=1)
    hold_nll_t1 = nll(hold, 1.0)

    if args.policy:
        policy_path = Path(args.policy)
    else:
        policy_path = Path(__file__).parent.parent.parent / "config" / "policy.v1.json"
    with open(policy_path, "r") as f:
        policy = json.load(f)

    policy["calibration"] = {
        "temperature": temperature,
        "status": "fitted",
        "method": "temperature scaling: p = sigmoid(score_milli/1000/T); "
                  "T via log-grid search + golden-section refinement on train NLL",
        "fitted_on": str(data_path),
        "fitted_at": datetime.now(timezone.utc).isoformat(),
        "n_train": len(train),
        "n_holdout": len(hold),
        "train_nll": train_nll,
        "holdout_nll": hold_nll,
        "holdout_nll_at_T1": hold_nll_t1,
        "seed": args.seed,
        "min_samples": args.min_samples,
    }
    with open(policy_path, "w") as f:
        json.dump(policy, f, indent=2)

    print(f"Fitted temperature T = {temperature:.4f}")
    print(f"  train:   n={len(train):d}  NLL={train_nll:.4f}")
    print(f"  holdout: n={len(hold):d}  NLL={hold_nll:.4f} (T=1 baseline: {hold_nll_t1:.4f})")
    if hold_nll >= hold_nll_t1:
        print("  WARNING: fitted T does not beat T=1 on holdout. Treat the fit as suspect; "
              "collect more labeled data before trusting it.")
    print(f"  wrote calibration block to {policy_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
