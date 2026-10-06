from aegis.detect.roles import determine_roles

def test_roles_approval():
    tx = {"from": "0xinit", "to": "0xtoken"}
    decoded = {"authorization_list": []}
    effects = [{"kind": "erc20_approval", "from_": "0xowner", "to": "0xspender"}]
    sig_effects = []
    
    sub, init = determine_roles(tx, decoded, effects, sig_effects)
    assert sub == "0xowner"
    assert init == "0xinit"

def test_roles_7702():
    tx = {"from": "0xinit", "to": "0xtarget"}
    decoded = {"authorization_list": [{"authority": "0xauth"}]}
    effects = []
    sig_effects = []
    
    sub, init = determine_roles(tx, decoded, effects, sig_effects)
    assert sub == "0xauth"
    assert init == "0xinit"

def test_roles_seaport():
    tx = {"from": "0xinit", "to": "0xtarget"}
    decoded = {"authorization_list": []}
    effects = []
    sig_effects = [{"type": "seaport_order", "offerer": "0xofferer"}]
    
    sub, init = determine_roles(tx, decoded, effects, sig_effects)
    assert sub == "0xofferer"
    assert init == "0xinit"

def test_roles_transfer():
    tx = {"from": "0xinit", "to": "0xtoken"}
    decoded = {"authorization_list": []}
    effects = [{"kind": "erc20_transfer", "from_": "0xsender", "to": "0xrecv", "token": "0xtoken"}]
    sig_effects = []
    
    sub, init = determine_roles(tx, decoded, effects, sig_effects)
    assert sub == "0xsender"
    assert init == "0xinit"
    
def test_roles_fallback():
    tx = {"from": "0xinit", "to": "0xtarget"}
    decoded = {"authorization_list": []}
    effects = [{"kind": "erc20_transfer", "from_": "0xsender", "to": "0xrecv", "token": "0xother"}]
    sig_effects = []
    
    sub, init = determine_roles(tx, decoded, effects, sig_effects)
    assert sub == "0xinit"
    assert init == "0xinit"
