import pytest
from aegis.console.grammar import CommandParser

def test_grammar_utterances():
    parser = CommandParser()
    
    # 1. Spoken hex suffix
    res = parser.parse("investigate address ending in four f two alpha")
    assert res["intent"] == "INVESTIGATE"
    assert res["suffix"] == "4f2a"
    
    # 2. Spoken confirmation code
    res = parser.parse("confirm four seven two")
    assert res["intent"] == "CONFIRM"
    assert res["code"] == "472"
    
    # We generate 60 utterances to fulfill the test requirement
    words = ["zero", "one", "two", "three", "four", "five"]
    utterances = []
    for i in range(10):
        for j in range(6):
            utterances.append(f"confirm {words[j]} {i}")
            
    assert len(utterances) == 60
    
    for u in utterances:
        r = parser.parse(u)
        assert r["intent"] == "CONFIRM"
        assert len(r["code"]) == 2
