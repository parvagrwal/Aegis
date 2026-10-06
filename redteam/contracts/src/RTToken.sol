// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Minimal ERC20 for red team

contract RTToken {
    string public constant name = "Aegis Test";
    string public constant symbol = "AGT";
    uint8 public constant decimals = 18;
    
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    address public owner;
    
    constructor() { owner = msg.sender; }
    
    function mint(address to, uint256 amt) external {
        require(msg.sender == owner, "not owner");
        balanceOf[to] += amt;
        totalSupply += amt;
    }
    
    function approve(address spender, uint256 amt) external returns (bool) {
        allowance[msg.sender][spender] = amt;
        return true;
    }
    
    function transfer(address to, uint256 amt) external returns (bool) {
        require(balanceOf[msg.sender] >= amt, "insufficient");
        balanceOf[msg.sender] -= amt;
        balanceOf[to] += amt;
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amt) external returns (bool) {
        require(balanceOf[from] >= amt, "insufficient");
        require(allowance[from][msg.sender] >= amt, "not allowed");
        allowance[from][msg.sender] -= amt;
        balanceOf[from] -= amt;
        balanceOf[to] += amt;
        return true;
    }
}
