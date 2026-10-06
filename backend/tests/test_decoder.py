import json
from pathlib import Path
from aegis.chain.decoder import decode_tx
from aegis.chain.typed_data import decode_typed

def load_tx(name: str) -> dict:
    p = Path(__file__).parent / "data" / f"{name}.json"
    with open(p, "r") as f:
        return json.load(f)

def test_decode_approve():
    tx = load_tx("approve")
    decoded = decode_tx(tx)
    assert decoded["signature"] == "approve(address,uint256)"
    assert decoded["args"]["spender"] == "0xdef1c0ded9bec7f1a1670819833240f027b25eff"
    assert decoded["args"]["amount"] == 1000000000000000000

def test_decode_setApprovalForAll():
    tx = load_tx("setApprovalForAll")
    decoded = decode_tx(tx)
    assert decoded["signature"] == "setApprovalForAll(address,bool)"
    assert decoded["args"]["operator"] == "0xdef1c0ded9bec7f1a1670819833240f027b25eff"
    assert decoded["args"]["approved"] == True

def test_decode_create():
    tx = load_tx("create")
    decoded = decode_tx(tx)
    assert decoded["is_create"] is True

def test_decode_type4():
    tx = load_tx("type4")
    decoded = decode_tx(tx)
    assert decoded["type"] == 4
    assert len(decoded["authorization_list"]) == 1
    # We used dummy signature values, so the recovered authority will be None due to invalid point
    assert decoded["authorization_list"][0]["authority"] is None

def test_typed_data_permit():
    td = {
        "primaryType": "Permit",
        "domain": {"verifyingContract": "0xtoken", "chainId": 1},
        "message": {"owner": "0xA", "spender": "0xB", "value": "100"}
    }
    decoded = decode_typed(td, request_chain_id=1, message_token="0xtoken")
    assert not decoded["domain_mismatch"]
    assert decoded["effects"][0]["type"] == "permit"

    decoded_mismatch = decode_typed(td, request_chain_id=2, message_token="0xwrong")
    assert decoded_mismatch["domain_mismatch"]

def test_typed_data_permit2():
    td = {
        "primaryType": "PermitSingle",
        "domain": {"chainId": 1},
        "message": {
            "details": {"token": "0xT", "amount": "100", "expiration": "999"},
            "spender": "0xS"
        }
    }
    decoded = decode_typed(td)
    assert decoded["effects"][0]["type"] == "permit2"
    assert decoded["effects"][0]["token"] == "0xT"
