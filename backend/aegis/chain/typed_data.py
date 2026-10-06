class DecodedSignature(dict):
    pass

def decode_typed(td: dict, request_chain_id: int = None, message_token: str = None) -> DecodedSignature:
    domain = td.get("domain", {})
    message = td.get("message", {})
    primary_type = td.get("primaryType", "")

    domain_mismatch = False
    
    # EIP-2612 checking
    if primary_type == "Permit":
        # domain.verifyingContract should match the token contract where the permit is used
        verifying_contract = domain.get("verifyingContract", "").lower()
        if message_token and verifying_contract != message_token.lower():
            domain_mismatch = True

    # General chainId checking
    domain_chain = domain.get("chainId")
    if domain_chain is not None and request_chain_id is not None:
        if int(domain_chain) != int(request_chain_id):
            domain_mismatch = True

    effects = []
    
    if primary_type == "Permit":
        effects.append({
            "type": "permit",
            "owner": message.get("owner"),
            "spender": message.get("spender"),
            "value": message.get("value"),
            "deadline": message.get("deadline")
        })
    elif primary_type == "PermitSingle":
        details = message.get("details", {})
        effects.append({
            "type": "permit2",
            "token": details.get("token"),
            "amount": details.get("amount"),
            "expiration": details.get("expiration"),
            "spender": message.get("spender")
        })
    elif primary_type == "PermitBatch":
        spender = message.get("spender")
        for detail in message.get("details", []):
            effects.append({
                "type": "permit2",
                "token": detail.get("token"),
                "amount": detail.get("amount"),
                "expiration": detail.get("expiration"),
                "spender": spender
            })
    elif primary_type == "PermitTransferFrom":
        permitted = message.get("permitted", {})
        effects.append({
            "type": "permit2_transfer",
            "token": permitted.get("token"),
            "amount": permitted.get("amount"),
            "spender": message.get("spender")
        })
    elif primary_type == "PermitBatchTransferFrom":
        spender = message.get("spender")
        for p in message.get("permitted", []):
            effects.append({
                "type": "permit2_transfer",
                "token": p.get("token"),
                "amount": p.get("amount"),
                "spender": spender
            })
    elif primary_type == "PermitWitnessTransferFrom":
        permitted = message.get("permitted", {})
        effects.append({
            "type": "permit2_transfer",
            "token": permitted.get("token"),
            "amount": permitted.get("amount"),
            "spender": message.get("spender")
        })
    elif primary_type == "OrderComponents":
        # Seaport
        effects.append({
            "type": "seaport_order",
            "offerer": message.get("offerer"),
            "offer": message.get("offer", []),
            "consideration": message.get("consideration", [])
        })

    return DecodedSignature({
        "primary_type": primary_type,
        "effects": effects,
        "domain_mismatch": domain_mismatch
    })
