import json

def adapt_cases(raw_data) -> list[dict]:
    if isinstance(raw_data, dict) and "cases" in raw_data:
        raw_data = raw_data["cases"]
    elif not isinstance(raw_data, list):
        return []
        
    out = []
    for i, item in enumerate(raw_data):
        case_id = str(item.get("id", item.get("case_id", f"case_{i}")))
        tx_hash = item.get("tx", item.get("tx_hash", item.get("hash", item.get("transaction"))))
        address = item.get("address", item.get("contract"))
        typed_data = item.get("typed_data", item.get("signature_request"))
        
        raw_label = str(item.get("label", item.get("ground_truth", item.get("class", "")))).lower()
        if raw_label in ("malicious", "phishing", "attack", "1", "true"):
            label = "malicious"
        elif raw_label in ("benign", "legit", "0", "false"):
            label = "benign"
        else:
            label = "unknown"
            
        raw_chain = str(item.get("chain", item.get("network", "ethereum"))).lower()
        if raw_chain in ("eth", "mainnet", "1"):
            chain = "ethereum"
        else:
            chain = raw_chain
            
        category = item.get("category", item.get("type", item.get("attack_type", "unknown")))
        source = item.get("source", "unknown")
        
        input_type = "unknown"
        if tx_hash:
            input_type = "tx"
        elif typed_data:
            input_type = "typed_data"
        elif address:
            input_type = "address"
            
        case = {
            "case_id": case_id,
            "chain": chain,
            "input_type": input_type,
            "label": label,
            "category": category,
            "source": source
        }
        
        if tx_hash: case["tx_hash"] = tx_hash
        if address: case["address"] = address
        if typed_data: case["typed_data"] = typed_data
        
        if input_type == "unknown":
            case["unresolvable"] = True
            
        out.append(case)
        
    return out
