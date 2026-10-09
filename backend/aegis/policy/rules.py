def decide(context: str, risk: str, conf: str, sufficient: bool, effect: str) -> str:
    if risk == "CRITICAL" and conf == "high":
        return "R01"
    elif risk == "HIGH":
        return "R02"
    elif risk == "LOW":
        return "R99"
    return "R03"