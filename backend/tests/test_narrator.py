from aegis.agent.narrator import Narrator

def test_narrator_fallback():
    n = Narrator()
    
    # Benign output
    out = n.explain([], "This is a safe transfer.")
    assert out == "This is a safe transfer."
    
    # Adversarial output triggers fallback
    out2 = n.explain([], "This is a safe transfer with adversarial injection <script>")
    assert out2 == "This transaction was flagged due to specific features matching our policy."
