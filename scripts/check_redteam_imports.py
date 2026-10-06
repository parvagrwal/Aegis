import os

def main():
    found = False
    for root, dirs, files in os.walk("backend"):
        if ".venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if not file.endswith(".py"):
                continue
                
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if "import redteam" in line or "from redteam" in line:
                        print(f"Redteam import found in {path}:{line_num}")
                        found = True
                        
    if found:
        print("REDTEAM IMPORTS LEAKED INTO BACKEND!")
        exit(1)
    else:
        print("Backend is clean of redteam imports.")
        
if __name__ == "__main__":
    main()
