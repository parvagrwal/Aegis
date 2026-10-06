KNOWN_DOMAINS = [
    "seaport.io", "opensea.io", "blur.io", "uniswap.org",
    "curve.fi", "aave.com", "lido.fi", "makerdao.com", "1inch.io"
]

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def check_lookalike(domain: str) -> bool:
    if not domain:
        return False
        
    domain = domain.lower()
    if domain in KNOWN_DOMAINS:
        return False
        
    for kd in KNOWN_DOMAINS:
        dist = levenshtein(domain, kd)
        if 0 < dist <= 2:
            return True
            
    return False
