import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from aegis.chain.explorer import ExplorerClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    if len(sys.argv) < 3:
        print("Usage: python run_tool.py profile <address>")
        sys.exit(1)
        
    cmd = sys.argv[1]
    addr = sys.argv[2]
    
    if cmd == "profile":
        client = ExplorerClient()
        res = await client.get_source(1, addr)
        await client.close()
        print(f"verified={res.get('verified', False)}")
        
if __name__ == "__main__":
    asyncio.run(main())
