import asyncio
import json
import os
import sys
try:
    import websockets
except ImportError:
    print("Please install websockets: pip install websockets")
    sys.exit(1)

async def firehose():
    api_key = os.environ.get("ALCHEMY_API_KEY")
    if not api_key:
        print("ERROR: ALCHEMY_API_KEY not found in environment.")
        return
        
    chain = "sepolia" if os.environ.get("WATCH_SEPOLIA", "1") == "1" else "mainnet"
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
