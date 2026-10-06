from aegis.agent.memory import Memory

def test_fingerprint():
    mem = Memory()
    fp1 = mem.generate_fingerprint({"to": "0x123", "input": "0xabcdef"})
    fp2 = mem.generate_fingerprint({"to": "0x123", "input": "0xabcdef"})
    fp3 = mem.generate_fingerprint({"to": "0x456", "input": "0x111111"})
    
    assert fp1 == fp2
    assert fp1 != fp3
    
    sim = mem.compute_similarity(fp1, fp2)
    assert sim == 1.0
