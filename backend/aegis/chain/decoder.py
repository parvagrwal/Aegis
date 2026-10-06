import eth_abi
import eth_abi.grammar
from hexbytes import HexBytes
from eth_utils import to_checksum_address
from eth_account import Account
import rlp
from eth_keys import keys
from eth_hash.auto import keccak
from aegis.chain.abi_registry import SELECTORS

class DecodedCall(dict):
    pass

def parse_signature_types(sig: str) -> list[str]:
    start = sig.find('(')
    if start == -1: return []
    args_str = sig[start:]
    t = eth_abi.grammar.parse(args_str)
    return [c.to_type_str() for c in t.components]

def recover_7702(chain_id: int, address: str, nonce: int, v: int, r: int, s: int) -> str:
    if hasattr(Account, 'recover_authorization'):
        # Just in case eth_account supports it in the future
        return Account.recover_authorization(chain_id, address, nonce, v, r, s)
    
    address_bytes = HexBytes(address)
    rlp_encoded = rlp.encode([chain_id, address_bytes, nonce])
    msg = b"\x05" + rlp_encoded
    msg_hash = keccak(msg)
    
    y_parity = v
    if y_parity >= 27:
        y_parity -= 27
        
    try:
        sig = keys.Signature(vrs=(y_parity, r, s))
        pub = sig.recover_public_key_from_msg_hash(msg_hash)
        return pub.to_checksum_address()
    except Exception:
        return None

def decode_tx(tx: dict) -> DecodedCall:
    inp = tx.get("input", "0x")
    if inp == "0x":
        inp_bytes = b""
    else:
        inp_bytes = HexBytes(inp)
        
    to_addr = tx.get("to")
    is_create = (to_addr is None or to_addr == "" or to_addr == "0x")
    
    tx_type_raw = tx.get("type", "0x0")
    tx_type = int(tx_type_raw, 16) if isinstance(tx_type_raw, str) else tx_type_raw
    
    auth_list = []
    if tx_type == 4 and "authorizationList" in tx:
        for auth in tx["authorizationList"]:
            chain_id = int(auth.get("chainId", "0x0"), 16)
            addr = auth.get("address", "0x0")
            nonce = int(auth.get("nonce", "0x0"), 16)
            v = int(auth.get("v", "0x0"), 16)
            r = int(auth.get("r", "0x0"), 16)
            s = int(auth.get("s", "0x0"), 16)
            
            authority = recover_7702(chain_id, addr, nonce, v, r, s)
            auth_list.append({
                "chain_id": chain_id,
                "address": addr,
                "nonce": nonce,
                "authority": authority
            })
            
    if len(inp_bytes) < 4:
        return DecodedCall({
            "selector": None,
            "signature": None,
            "args": {},
            "is_create": is_create,
            "type": tx_type,
            "authorization_list": auth_list
        })
        
    selector = "0x" + inp_bytes[:4].hex()
    args_data = inp_bytes[4:]
    
    if selector not in SELECTORS:
        return DecodedCall({
            "selector": selector,
            "signature": None,
            "args": {},
            "is_create": is_create,
            "type": tx_type,
            "authorization_list": auth_list
        })
        
    sig, arg_names = SELECTORS[selector]
    types = parse_signature_types(sig)
    
    try:
        decoded = eth_abi.decode(types, args_data)
        args_dict = dict(zip(arg_names, decoded))
    except Exception:
        args_dict = {}
        
    return DecodedCall({
        "selector": selector,
        "signature": sig,
        "args": args_dict,
        "is_create": is_create,
        "type": tx_type,
        "authorization_list": auth_list
    })
