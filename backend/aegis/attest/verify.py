import json
import httpx
import hashlib
from aegis.attest.anchor_evm import get_rpc_url
from eth_utils import keccak
from eth_abi import decode

def verify_attestation(case_id: str, local_result: dict) -> dict:
    rpc_url = get_rpc_url()
    tx_clean = case_id.strip().replace("0x", "")
    case_key = bytes.fromhex(tx_clean.zfill(64))[:32]
    
    # 1. Recompute the local hash
    # Note: in routes_scan.py we used:
    # result_json = json.dumps(result, sort_keys=True)
    # record_hash = hashlib.sha256(result_json.encode('utf-8')).digest()
    
    local_copy = local_result.copy()
    local_copy.pop("attestation_status", None)
    local_copy.pop("defense_status", None)
    
    result_json = json.dumps(local_copy, sort_keys=True)
    local_hash = hashlib.sha256(result_json.encode('utf-8')).digest().hex()
    
    # 2. Fetch the anchor contract state for this case_key
    # The AegisAttestor contract has a mapping(bytes32 => Record) public records;
    
    # Storage slot for mapping is 0. key is case_key.
    # Actually, we can just call the 
    selector = keccak(b"records(bytes32)")[:4]
    calldata = selector + case_key
    
    to_addr = "0x622E814975186227d21A12b105A1B7074649d6b6"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": to_addr,
            "data": "0x" + calldata.hex()
        }, "latest"],
        "id": 1
    }
    
    r = httpx.post(rpc_url, json=payload).json()
    if "error" in r or r["result"] == "0x":
        return {
            "verified": False,
            "on_chain_hash": None,
            "local_hash": "0x" + local_hash,
            "error": "Attestation not found on-chain."
        }
        
    # Decode the return data
    # (uint32 version, bytes32 recordHash, uint8 verdict, uint16 confidenceBps, uint48 timestamp)
    res_bytes = bytes.fromhex(r["result"][2:])
    try:
        decoded = decode(["uint32", "bytes32", "uint8", "uint16", "uint48"], res_bytes)
        on_chain_hash = decoded[1].hex()
        
        is_verified = (on_chain_hash == local_hash)
        return {
            "verified": is_verified,
            "on_chain_hash": "0x" + on_chain_hash,
            "local_hash": "0x" + local_hash
        }
    except Exception as e:
        return {
            "verified": False,
            "on_chain_hash": None,
            "local_hash": "0x" + local_hash,
            "error": f"Failed to decode on-chain data: {str(e)}"
        }
