import os
import httpx

def detect_solana_approve(tx_data: dict | str) -> list:
    features = []
    
    # If it's a dict (mock test), do the old logic
    if isinstance(tx_data, dict):
        if tx_data.get("type") == "SPL_APPROVE" and tx_data.get("delegate") not in ["KNOWN_DELEGATE"]:
            features.append({"id": "sol.token_approve_unknown_delegate", "weight": 2000})
        return features

    signature = tx_data
    # We use Alchemy Solana RPC if available, else standard public
    rpc_url = os.environ.get("SOLANA_RPC_URL")
    if not rpc_url:
        key = os.environ.get("ALCHEMY_API_KEY")
        if key:
            rpc_url = f"https://solana-mainnet.g.alchemy.com/v2/{key}"
        else:
            rpc_url = "https://api.mainnet-beta.solana.com"
            
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
        ]
    }
    
    try:
        r = httpx.post(rpc_url, json=payload, timeout=10.0).json()
        if "result" not in r or not r["result"]:
            return features
            
        tx = r["result"]["transaction"]
        message = tx["message"]
        
        # Look through instructions
        for ix in message.get("instructions", []):
            if ix.get("program") == "spl-token" and ix.get("parsed", {}).get("type") == "approve":
                info = ix["parsed"]["info"]
                delegate = info.get("delegate")
                owner = info.get("owner")
                amount = int(info.get("amount", 0))
                
                # Check against known safe delegates
                if delegate not in ["KNOWN_DELEGATE"]:
                    features.append({
                        "id": "sol.token_approve_unknown_delegate",
                        "weight": 2000,
                        "data": {"delegate": delegate, "owner": owner, "amount": amount}
                    })
    except Exception as e:
        pass
        
    return features
