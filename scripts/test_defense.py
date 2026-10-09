import asyncio
import os
import time
from aegis.api.routes_scan import live_scan
from aegis.agent.orchestrator import Orchestrator
from aegis.defend.queue import DefendQueue

async def main():
    print("=== AEGIS Agentic Defense E2E Test ===")
    if not os.environ.get("DEFENDER_PRIVATE_KEY"):
        print("ERROR: DEFENDER_PRIVATE_KEY not found in environment.")
        print("Please export your Sepolia private key to run the live defense revocation.")
        return

    print("1. Monitoring for malicious approval...")
    # This hash should be a real Sepolia transaction where a malicious approval was made
    tx_hash = input("Enter a malicious Sepolia tx_hash (or press Enter to use a default test hash): ").strip()
    if not tx_hash:
        tx_hash = "0x..." # User must provide
        
    print(f"\n2. Scanning {tx_hash}...")
    try:
        result = await live_scan(tx_hash, 11155111)
        print(f"Scan verdict: {result.get('verdict')}")
        
        if result.get("verdict") == "malicious":
            print("\n3. Triggering Autonomous Agent...")
            orchestrator = Orchestrator()
            res = await orchestrator.run(result)
            print("Agent loop finished.")
            
            executed = res.get("executed_actions", [])
            if executed:
                print("\n4. Defense Actions Executed On-Chain:")
                for act in executed:
                    print(f" - {act}")
                    
                # The executed action will have the tx_hash if we properly saved it
                queue = DefendQueue()
                # Get the latest executed action from SQLite
                import sqlite3
                from pathlib import Path
                db_path = Path(__file__).parent.parent / "queue.db"
                with sqlite3.connect(db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute("SELECT * FROM defend_queue WHERE status = 'executed' ORDER BY created_at DESC LIMIT 1").fetchall()
                    if rows:
                        print(f"\nSUCCESS! Revocation transaction broadcasted: {rows[0]['tx_hash']}")
                        print("Update your README with this transaction hash as evidence!")
            else:
                print("No defense actions were executed.")
    except Exception as e:
        print(f"Error during E2E test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
