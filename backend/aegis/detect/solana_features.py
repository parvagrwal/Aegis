def detect_solana_approve(tx_data: dict) -> list:
    features = []
    # Simplified check for Solana SPL token approve to unknown delegate
    if tx_data.get("type") == "SPL_APPROVE" and tx_data.get("delegate") not in ["KNOWN_DELEGATE"]:
        features.append({"id": "sol.token_approve_unknown_delegate", "weight": 2000})
    return features
