import json
from pathlib import Path
import random

def main():
    eval_dir = Path(__file__).parent
    cases_file = eval_dir / "cases.json"
    
    with open(cases_file, "r") as f:
        cases = json.load(f)
        
    # Pick a random 50% for dev set, or just use the first 15 since we only have 30
    dev_cases = cases[:15]
    
    with open(eval_dir / "dev_cases.json", "w") as f:
        json.dump(dev_cases, f, indent=2)
        
    print(f"Built dev_cases.json with {len(dev_cases)} cases")

if __name__ == "__main__":
    main()
