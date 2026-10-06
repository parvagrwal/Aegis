import pytest
from aegis.attest.record import canonical_serialize

def test_canonical_serialization():
    data1 = {"b": 2, "a": 1}
    data2 = {"a": 1, "b": 2}
    
    assert canonical_serialize(data1) == canonical_serialize(data2)
    assert canonical_serialize(data1) == b'{"a":1,"b":2}'
    
    with pytest.raises(TypeError, match="Floats are not allowed"):
        canonical_serialize({"a": 1.5})
        
    with pytest.raises(TypeError, match="Floats are not allowed"):
        canonical_serialize({"a": {"b": [1, 2.0]}})
