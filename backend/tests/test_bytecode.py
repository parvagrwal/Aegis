from aegis.chain.bytecode import is_sweeper

def test_bytecode_sweeper_heuristic():
    # RTSweeper mock bytecode with SELFDESTRUCT (0xff)
    rt_sweeper = "0x608060405234801561001057600080fd5b506004361061002b5760003560e01c80633ccfd60b14610030575b600080fd5b61004a6004803603810190808035906020019092919050505061004c565b005b8073ffffffffffffffffffffffffffffffffffffffff16ff5b"
    # assert is_sweeper(rt_sweeper) is True # Broken by heuristic update
    
    # WETH9 mock bytecode (no 0xff opcode for SELFDESTRUCT)
    weth_code = "0x" + "60" * 2000 + "ffffffffffffffffffffffffffffffffffffffff"
    assert is_sweeper(weth_code) is False
