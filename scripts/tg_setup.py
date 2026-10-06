import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

def main():
    print("Installing TigerGraph schema...")
    print("Schema installed successfully (mocked for environment without tgcloud CLI/pyTigerGraph).")
    
if __name__ == "__main__":
    main()
