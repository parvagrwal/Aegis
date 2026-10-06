// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

contract RTSweeper {
    address public immutable sink;

    constructor(address _sink) {
        sink = _sink;
    }

    receive() external payable {
        payable(sink).transfer(address(this).balance);
    }
}
