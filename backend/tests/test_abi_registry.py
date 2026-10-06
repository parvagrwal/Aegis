from aegis.chain.abi_registry import SELECTORS, EVENTS, sig_to_selector, sig_to_topic

def test_abi_registry_selectors():
    # Verify that the hardcoded selectors match the computed keccak of their signatures
    for sel, (sig, args) in SELECTORS.items():
        assert sel == sig_to_selector(sig), f"Selector {sel} does not match computed hash for {sig}"

def test_abi_registry_events():
    for topic, sig in EVENTS.items():
        assert topic == sig_to_topic(sig), f"Topic {topic} does not match computed hash for {sig}"
