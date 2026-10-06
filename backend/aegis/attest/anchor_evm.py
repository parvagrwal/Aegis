import os
import httpx
import time
from eth_account import Account
from eth_abi import encode

def get_rpc_url():
    return f"https://eth-sepolia.g.alchemy.com/v2/{os.environ.get('ALCHEMY_API_KEY')}"
    
def get_nonce(address: str) -> int:
    payload = {"jsonrpc":"2.0","method":"eth_getTransactionCount","params":[address, "latest"],"id":1}
    r = httpx.post(get_rpc_url(), json=payload).json()
    return int(r["result"], 16)

def get_gas_price() -> int:
    payload = {"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}
    r = httpx.post(get_rpc_url(), json=payload).json()
    return int(r["result"], 16)

def anchor_records(case_keys: list[bytes], versions: list[int], record_hashes: list[bytes], verdicts: list[int], confs: list[int]):
    pk = os.environ.get("ATTESTER_PRIVATE_KEY")
    if not pk:
        raise ValueError("ATTESTER_PRIVATE_KEY not set")
        
    acct = Account.from_key(pk)
    
    # encode data for: function attest(bytes32[] calldata caseKeys, uint32[] calldata versions, bytes32[] calldata recordHashes, uint8[] calldata verdicts, uint16[] calldata confidenceBps)
    # selector: 0xeb121b6a -> keccak256("attest(bytes32[],uint32[],bytes32[],uint8[],uint16[])")[:4]
    selector = bytes.fromhex("34ab03d7") # Wait, let's calculate the real selector in the test or manually
    # Actually, I'll calculate it inline or use eth_utils.keccak(b"attest(bytes32[],uint32[],bytes32[],uint8[],uint16[])")[:4]
    from eth_utils import keccak
    selector = keccak(b"attest(bytes32[],uint32[],bytes32[],uint8[],uint16[])")[:4]
    
    calldata = selector + encode(
        ["bytes32[]", "uint32[]", "bytes32[]", "uint8[]", "uint16[]"],
        [case_keys, versions, record_hashes, verdicts, confs]
    )
    
    tx = {
        "to": "0x622E814975186227d21A12b105A1B7074649d6b6", # AegisAttestor
        "value": 0,
        "gas": 200000,
        "gasPrice": int(get_gas_price() * 1.5),
        "nonce": get_nonce(acct.address),
        "chainId": 11155111,
        "data": calldata,
    }
    
    signed = acct.sign_transaction(tx)
    
    payload = {"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":[signed.raw_transaction.hex()],"id":1}
    r = httpx.post(get_rpc_url(), json=payload).json()
    
    if "error" in r:
        raise Exception(f"Tx failed: {r['error']}")
        
    tx_hash = r["result"]
    return tx_hash
