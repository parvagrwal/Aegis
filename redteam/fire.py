import sys
import time

def main():
    scenario = "benign_transfer"
    if "--scenario" in sys.argv:
        scenario = sys.argv[sys.argv.index("--scenario") + 1]
    elif len(sys.argv) > 1:
        scenario = sys.argv[1]
        
    print(f"Firing scenario: {scenario}")
    
    if scenario == "benign_transfer":
        print("Mined tx: 0xbenigntransfer123")
    elif scenario == "approve_drainer":
        print("Mined tx: 0xapprovedrainer123")
    else:
        print("Unknown scenario")

if __name__ == "__main__":
    main()
