from aegis.models.case import CaseContext

def triage(ctx: CaseContext) -> str:
    # 7.7 Triage points mapping
    # Determine basic status: ASSETS_MOVED, DELEGATION_ACTIVE, APPROVAL_ACTIVE, POISONING, NONE
    
    outflow = False
    inflow = False
    subj_flows = ctx.net_flows.get(ctx.subject, {})
    for t, amt in subj_flows.items():
        if amt < 0: outflow = True
        if amt > 0: inflow = True
        
    if outflow and not inflow:
        return "ASSETS_MOVED"
        
    if ctx.decoded.get("type") == 4:
        return "DELEGATION_ACTIVE"
        
    for eff in ctx.effects:
        if eff.get("kind") in ("erc20_approval", "nft_approval_all", "permit2_approval"):
            if int(eff.get("amount", "0")) > 0 or eff.get("amount") == "MAX":
                return "APPROVAL_ACTIVE"
                
    return "NONE"
