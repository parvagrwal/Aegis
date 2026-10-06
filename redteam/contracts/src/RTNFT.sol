// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

contract RTNFT {
    mapping(uint256 => address) public ownerOf;
    mapping(uint256 => address) public getApproved;
    mapping(address => mapping(address => bool)) public isApprovedForAll;
    
    address public owner;
    uint256 public nextId;
    
    constructor() { owner = msg.sender; }
    
    function mint(address to) external {
        require(msg.sender == owner, "not owner");
        ownerOf[nextId++] = to;
    }
    
    function approve(address to, uint256 tokenId) external {
        require(msg.sender == ownerOf[tokenId], "not owner");
        getApproved[tokenId] = to;
    }
    
    function setApprovalForAll(address operator, bool approved) external {
        isApprovedForAll[msg.sender][operator] = approved;
    }
    
    function transferFrom(address from, address to, uint256 tokenId) external {
        require(ownerOf[tokenId] == from, "wrong owner");
        require(msg.sender == from || getApproved[tokenId] == msg.sender || isApprovedForAll[from][msg.sender], "not allowed");
        ownerOf[tokenId] = to;
    }
}
