// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import "./RTDrainer.sol";

contract RTFactory {
    event Deployed(address drainer);
    
    function deploy(bytes32 salt, address a, address b) external returns (address) {
        address drainer = address(new RTDrainer{salt: salt}(a, b));
        emit Deployed(drainer);
        return drainer;
    }
}
