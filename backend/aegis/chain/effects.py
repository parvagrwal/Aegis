from typing import Optional

class Effect(dict):
    pass

def effects_from_logs(logs: list[dict]) -> list[Effect]:
    effects = []
    
    # Simple ERC20/721/Native Transfer parser based on section 7.6
    # ERC20 Transfer: Topic 0 = 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
    TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    APPROVAL_TOPIC = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
    APPROVAL_FOR_ALL = "0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31"
    
    for log in logs:
        topics = log.get("topics", [])
        if not topics: continue
        
        t0 = topics[0]
        address = log.get("address", "").lower()
        
        # Native ETH transfers via Alchemy are reported with 0xeeeeeeee...
        if address == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee" and t0 == TRANSFER_TOPIC:
            if len(topics) >= 3:
                from_ = "0x" + topics[1][26:]
                to = "0x" + topics[2][26:]
                data = log.get("data", "0x")
                amount = str(int(data, 16)) if data != "0x" else "0"
                effects.append(Effect({
                    "kind": "native_transfer",
                    "token": address,
                    "from_": from_,
                    "to": to,
                    "amount": amount,
                    "token_id": None,
                    "usd_cents": -1
                }))
        elif t0 == TRANSFER_TOPIC:
            if len(topics) == 3:
                # ERC20
                from_ = "0x" + topics[1][26:]
                to = "0x" + topics[2][26:]
                data = log.get("data", "0x")
                amount = str(int(data, 16)) if data != "0x" else "0"
                effects.append(Effect({
                    "kind": "erc20_transfer",
                    "token": address,
                    "from_": from_,
                    "to": to,
                    "amount": amount,
                    "token_id": None,
                    "usd_cents": -1
                }))
            elif len(topics) == 4:
                # ERC721
                from_ = "0x" + topics[1][26:]
                to = "0x" + topics[2][26:]
                token_id = str(int(topics[3], 16))
                effects.append(Effect({
                    "kind": "nft_transfer",
                    "token": address,
                    "from_": from_,
                    "to": to,
                    "amount": "1",
                    "token_id": token_id,
                    "usd_cents": -1
                }))
                
        elif t0 == APPROVAL_TOPIC and len(topics) >= 3:
            owner = "0x" + topics[1][26:]
            spender = "0x" + topics[2][26:]
            data = log.get("data", "0x")
            amount = str(int(data, 16)) if data != "0x" else "0"
            effects.append(Effect({
                "kind": "erc20_approval",
                "token": address,
                "from_": owner,
                "to": spender,
                "amount": amount,
                "token_id": None,
                "usd_cents": -1
            }))
            
        elif t0 == APPROVAL_FOR_ALL and len(topics) >= 3:
            owner = "0x" + topics[1][26:]
            operator = "0x" + topics[2][26:]
            data = log.get("data", "0x")
            # Usually bool in data
            is_approved = int(data, 16) != 0 if len(data) >= 66 else False
            if is_approved:
                effects.append(Effect({
                    "kind": "nft_approval_all",
                    "token": address,
                    "from_": owner,
                    "to": operator,
                    "amount": "MAX",
                    "token_id": None,
                    "usd_cents": -1
                }))
                
    return effects

def net_flows(effects: list[Effect]) -> dict[str, dict[str, int]]:
    flows = {}
    for eff in effects:
        if eff.get("kind") not in ("native_transfer", "erc20_transfer"):
            continue
            
        token = eff["token"]
        amount = int(eff["amount"])
        f = eff["from_"]
        t = eff["to"]
        
        if f not in flows: flows[f] = {}
        if token not in flows[f]: flows[f][token] = 0
        flows[f][token] -= amount
        
        if t not in flows: flows[t] = {}
        if token not in flows[t]: flows[t][token] = 0
        flows[t][token] += amount
        
    return flows
