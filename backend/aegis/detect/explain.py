def explain_features(features: list) -> list:
    explanations = []
    
    mapping = {
        "sim.large_value_transfer": "A massive volume of funds (+) was transferred in a single transaction, typical of protocol-level drains.",
        "intel.label_malicious": "One or more addresses involved are known malicious actors according to our threat intelligence.",
        "sim.subject_outflow_no_inflow": "The subject drained funds with no corresponding inflow - a classic extraction pattern.",
        "sim.approval_unlimited_to_eoa": "An unlimited ERC20 approval was granted to an Externally Owned Account (EOA), heavily indicating a phishing drainer.",
        "sim.sweeper_pattern": "Funds were swept from a compromised wallet to an aggregator address in a zero-value or automated fashion.",
        "sim.contract_creation_funded_by_tornado": "A new contract was deployed by an address previously funded by Tornado Cash."
    }
    
    for feat in features:
        if isinstance(feat, str):
            fid = feat
        else:
            fid = feat.get("id", "")
            
        if fid in mapping:
            explanations.append(mapping[fid])
        else:
            explanations.append(f"Triggered heuristic: {fid}")
            
    return explanations
