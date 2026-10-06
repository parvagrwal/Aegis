from typing import Optional

def determine_roles(tx: dict, decoded: dict, effects: list[dict], signature_effects: list[dict]) -> tuple[Optional[str], Optional[str]]:
    """
    Returns (subject, initiator).
    Rules for subject (from section 7.6):
    1. owner of an approval or permit effect
    2. the 7702 authority
    3. the from_ of a transfer effect if the tx.to is the token
    4. the seaport offerer
    5. tx.from
    """
    initiator = tx.get("from", "").lower()
    
    # 1. Approval or permit owner
    for eff in effects:
        if eff.get("kind") in ("erc20_approval", "nft_approval_all", "permit2_approval", "delegation"):
            return eff.get("from_"), initiator
            
    for sig_eff in signature_effects:
        if sig_eff.get("type") in ("permit", "permit2", "permit2_transfer"):
            return sig_eff.get("owner", sig_eff.get("from_", initiator)), initiator
        if sig_eff.get("type") == "seaport_order":
            return sig_eff.get("offerer"), initiator
            
    # 2. 7702 authority
    auth_list = decoded.get("authorization_list", [])
    if auth_list:
        auth = auth_list[0].get("authority")
        if auth: return auth.lower(), initiator
        
    # 3. transfer effect if tx.to is token
    tx_to = tx.get("to", "").lower()
    for eff in effects:
        if eff.get("kind") in ("erc20_transfer", "nft_transfer", "native_transfer"):
            if eff.get("token") == tx_to:
                return eff.get("from_"), initiator
                
    # 5. tx.from
    return initiator, initiator
