import asyncio
import json
import os
import sys

# Ensure backend module is resolvable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

try:
    from aegis.api.live_scan import live_scan, Unrunnable
except ImportError:
    print("Ensure you are running this from the project root or backend is in PYTHONPATH")
    sys.exit(1)

try:
    import websockets
except ImportError:
    print("Please install websockets: pip install websockets")
    sys.exit(1)

# Concurrency limiting for scans
semaphore = asyncio.Semaphore(10)

async def scan_transaction(tx_hash: str, chain_id: int):
    async with semaphore:
        try:
            # We add a slight delay since mempool transactions sometimes take a moment
            # to be fetchable via eth_getTransactionByHash even after the notification
            await asyncio.sleep(0.5)
            
            res = await live_scan(tx_hash, chain_id, timeout_s=10.0)
            verdict = res.get("verdict", "uncertain")
            score = res.get("score", 0)
            
            if verdict == "malicious":
                print(f"      [!] MALICIOUS ACTIVITY DETECTED! {tx_hash} | Score: {score}")
                print(f"      [!] Reasons: {res.get('reasons')}")
            elif verdict == "benign":
                print(f"   -> [BENIGN] {tx_hash} | Score: {score}")
            # we can suppress uncertain to keep logs clean, or print it
            
        except Unrunnable as e:
            # Pending transactions might not be fetchable immediately, ignore these
            pass
        except Exception as e:
            pass

async def firehose():
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("ALCHEMY_API_KEY")
    if not api_key:
        print("ERROR: ALCHEMY_API_KEY not found in environment.")
        return
        
    chain = "sepolia" if os.environ.get("WATCH_SEPOLIA", "1") == "1" else "mainnet"
    chain_id = 11155111 if chain == "sepolia" else 1
    ws_url = f"wss://eth-{chain}.g.alchemy.com/v2/{api_key}"
    
    subscribe_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": ["newPendingTransactions"]
    }

    print(f"[*] Connecting to Alchemy WebSocket ({chain})...")
    
    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                print("[+] Connected!")
                await ws.send(json.dumps(subscribe_payload))
                response = await ws.recv()
                print(f"[*] Subscribed: {response}")
                
                count = 0
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if "params" in data:
                        tx_hash = data["params"]["result"]
                        print(f"[{count}] Pending TX: {tx_hash}")
                        
                        # Fire and forget the background scan
                        asyncio.create_task(scan_transaction(tx_hash, chain_id))
                        
                        count += 1
        except websockets.exceptions.ConnectionClosed:
            print("[-] Connection closed. Reconnecting in 3s...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"[-] Error: {e}")
            await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        asyncio.run(firehose())
    except KeyboardInterrupt:
        print("\nExiting firehose.")
