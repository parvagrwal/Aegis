from eth_hash.auto import keccak

def sig_to_selector(sig: str) -> str:
    return "0x" + keccak(sig.encode('utf-8'))[:4].hex()

def sig_to_topic(sig: str) -> str:
    return "0x" + keccak(sig.encode('utf-8')).hex()

# Section 7.4 Table
SELECTORS: dict[str, tuple[str, list[str]]] = {
    "0x095ea7b3": ("approve(address,uint256)", ["spender", "amount"]),
    "0x39509351": ("increaseAllowance(address,uint256)", ["spender", "addedValue"]),
    "0xa9059cbb": ("transfer(address,uint256)", ["to", "amount"]),
    "0x23b872dd": ("transferFrom(address,address,uint256)", ["from", "to", "amount"]),
    "0xa22cb465": ("setApprovalForAll(address,bool)", ["operator", "approved"]),
    "0xd505accf": ("permit(address,address,uint256,uint256,uint8,bytes32,bytes32)", ["owner", "spender", "value", "deadline", "v", "r", "s"]),
    "0x2b67b570": ("permit(address,((address,uint160,uint48,uint48),address,uint256),bytes)", ["owner", "permitSingle", "signature"]),
    "0x2a2d80d1": ("permit(address,((address,uint160,uint48,uint48)[],address,uint256),bytes)", ["owner", "permitBatch", "signature"]),
    "0x30f28b7a": ("permitTransferFrom(((address,uint256),uint256,uint256),(address,uint256),address,bytes)", ["permit", "transferDetails", "owner", "signature"]),
    "0x137c29fe": ("permitWitnessTransferFrom(((address,uint256),uint256,uint256),(address,uint256),address,bytes32,string,bytes)", ["permit", "transferDetails", "owner", "witness", "witnessTypeString", "signature"]),
    "0x87517c45": ("approve(address,address,uint160,uint48)", ["token", "spender", "amount", "expiration"]),
    "0xcc53287f": ("lockdown((address,address)[])", ["approvals"]),
    "0x36c78516": ("transferFrom(address,address,uint160,address)", ["from", "to", "amount", "token"]),
}

BAIT_SIGNATURES = [
    "Claim()", "claim()", "SecurityUpdate()", "ClaimReward()", 
    "ClaimRewards()", "Connect()", "Execute()", "Verify()"
]

for sig in BAIT_SIGNATURES:
    sel = sig_to_selector(sig)
    SELECTORS[sel] = (sig, [])

EVENT_SIGNATURES = [
    "Transfer(address,address,uint256)",
    "Approval(address,address,uint256)",
    "ApprovalForAll(address,address,bool)",
    "TransferSingle(address,address,address,uint256,uint256)",
    "TransferBatch(address,address,address,uint256[],uint256[])",
    "Permit(address,address,address,uint160,uint48,uint48)",
    "Approval(address,address,address,uint160,uint48)",
    "FlashLoan(address,address,address,uint256,uint8,uint256,uint16)",
    "FlashLoan(address,address,uint256,uint256)",
    "Flash(address,address,uint256,uint256,uint256,uint256)"
]

EVENTS: dict[str, str] = {sig_to_topic(sig): sig for sig in EVENT_SIGNATURES}
