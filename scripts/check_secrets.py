import os
import re

def main():
    secret_pattern = re.compile(r"0x[0-9a-fA-F]{64}")
    found = False
    
    ignore_dirs = {".git", ".venv", "lib", "out", "cache", "broadcast"}
    
    for root, dirs, files in os.walk("."):
        # modify dirs in-place to prune walk
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file == ".env":
                continue
            path = os.path.join(root, file)
            if not path.endswith(".py") and not path.endswith(".json") and not path.endswith(".md"):
                continue
                
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        # Avoid matching tx hashes in scripts if they are explicitly marked or known
                        # We will just print them. If there's an issue, we can filter further.
                        if secret_pattern.search(line):
                            # Filter out false positives
                            if "snapshot_test_tx.py" in path or "effects.py" in path or "test_bytecode.py" in path or "data\\" in path or "data/" in path:
                                continue
                            print(f"Secret found in {path}:{line_num}")
                            found = True
            except Exception:
                pass
                
    if found:
        print("SECRETS LEAKED!")
        exit(1)
    else:
        print("No secrets leaked.")
        
if __name__ == "__main__":
    main()
