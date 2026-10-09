import os
import httpx
from eth_account import Account
from eth_abi import encode
from aegis.agent.permissions import check_permission
from eth_utils import to_checksum_address

class ToolError(Exception):
    pass

def revoke_approval(role: str, chain_id: int, token: str, spender: str):
    if not check_permission(role, "revoke_approval", chain_id):
        raise ToolError("Permission denied")
        
    pk = os.environ.get("DEFENDER_PRIVATE_KEY") or os.environ.get("ATTESTER_PRIVATE_KEY")
    if not pk:
        raise ToolError("No private key configured for revocations")
        
    acct = Account.from_key(pk)
    
    try:
        spender_addr = to_checksum_address(spender)
        token_addr = to_checksum_address(token)
    except Exception:
        raise ToolError("Invalid addresses provided")
        
    # approve(address,uint256) selector is 0x095ea7b3
    selector = bytes.fromhex("095ea7b3")
    calldata = selector + encode(["address", "uint256"], [spender_addr, 0])
    
    rpc_url = os.environ.get("AEGIS_RPC_URL", "https://eth-sepolia.g.alchemy.com/v2/" + os.environ.get("ALCHEMY_API_KEY", ""))
    
    # Get nonce
    nonce_r = httpx.post(rpc_url, json={"jsonrpc":"2.0","method":"eth_getTransactionCount","params":[acct.address, "latest"],"id":1}).json()
    nonce = int(nonce_r["result"], 16)
    
    # Get gas price
    gas_r = httpx.post(rpc_url, json={"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}).json()
    gas_price = int(gas_r["result"], 16)
    
    tx = {
        "to": token_addr,
        "value": 0,
        "gas": 100000,
        "gasPrice": int(gas_price * 1.5),
        "nonce": nonce,
        "chainId": chain_id,
        "data": calldata,
    }
    
    signed = acct.sign_transaction(tx)
    r = httpx.post(rpc_url, json={"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":[signed.raw_transaction.hex()],"id":1}).json()
    
    if "error" in r:
        raise ToolError(f"Tx failed: {r['error']}")
        
    return {"status": "broadcasted", "tx_hash": r["result"]}
    
def get_tools_for_role(role: str):
    if role == "narrator":
        return []
    return [revoke_approval]
