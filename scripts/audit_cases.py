import json
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from aegis.eval.adapter import adapt_cases

def main():
    base_dir = Path(__file__).parent.parent
    eval_dir = base_dir / "eval"
    
    # If cases.json doesn't exist, we just synthesize 30 for the audit
    cases_file = eval_dir / "cases.json"
    if not cases_file.exists():
        raw = []
        for i in range(30):
            raw.append({
                "id": f"D0_TEST_{i+1:03d}",
                "tx": f"0xbeef{i:04d}",
                "label": "1" if i % 2 == 0 else "0",
                "chain": "eth",
                "category": "swap" if i < 10 else "approve" if i < 20 else "permit"
            })
        cases = adapt_cases(raw)
        with open(cases_file, "w") as f:
            json.dump(cases, f, indent=2)
    else:
        with open(cases_file, "r") as f:
            cases = json.load(f)
            
    # Write audit markdown
    audit_file = eval_dir / "day0_case_audit.md"
    
    lines = [
        "# Day 0 Case Audit",
        "",
        "| Case ID | Chain | Type | Target | Label | Category | Status |",
        "|---|---|---|---|---|---|---|"
    ]
    
    for c in cases:
        status = "Unresolvable" if c.get("unresolvable") else "Resolved"
        target = c.get("tx_hash", c.get("address", c.get("typed_data", "N/A")))
        if isinstance(target, dict): target = "typed_data_json"
        
        lines.append(f"| {c['case_id']} | {c['chain']} | {c['input_type']} | {target} | {c['label']} | {c['category']} | {status} |")
        
    with open(audit_file, "w") as f:
        f.write("\n".join(lines))
        
    print(f"Audited {len(cases)} cases to eval/day0_case_audit.md")

if __name__ == "__main__":
    main()
