from aegis.models.case import CaseContext

def build_upsert(ctx: CaseContext) -> dict:
    vertices = {
        "Address": {},
        "DefenseCase": {},
    }
    edges = {
        "DefenseCase": {},
        "Address": {}
    }
    
    # Write subject
    vertices["Address"][ctx.subject] = {"chain": {"value": "ethereum"}, "kind": {"value": ctx.profiles.get(ctx.subject, {}).get("kind", "eoa")}}
    
    # Write beneficiary if any
    for eff in ctx.effects:
        if eff.get("to"):
            vertices["Address"][eff["to"]] = {"chain": {"value": "ethereum"}, "kind": {"value": ctx.profiles.get(eff["to"], {}).get("kind", "eoa")}}
            
            # Simple transfer edge
            if eff.get("kind") in ("erc20_transfer", "native_transfer", "nft_transfer"):
                f = eff.get("from_", ctx.subject)
                t = eff.get("to")
                
                if f not in edges["Address"]:
                    edges["Address"][f] = {"TRANSFER": {"Address": {}}}
                if "TRANSFER" not in edges["Address"][f]:
                    edges["Address"][f]["TRANSFER"] = {"Address": {}}
                    
                edges["Address"][f]["TRANSFER"]["Address"][t] = {
                    "token": {"value": eff.get("token", "")},
                    "amount": {"value": eff.get("amount", "0")}
                }
                
    # Add DefenseCase vertex
    vertices["DefenseCase"][ctx.case_id] = {
        "version": {"value": 1},
        "category": {"value": "eval"}
    }
    
    edges["DefenseCase"][ctx.case_id] = {
        "INVOLVES": {
            "Address": {
                ctx.subject: {"role": {"value": "subject"}},
                ctx.initiator: {"role": {"value": "initiator"}}
            }
        }
    }
    
    return {"vertices": vertices, "edges": edges}
