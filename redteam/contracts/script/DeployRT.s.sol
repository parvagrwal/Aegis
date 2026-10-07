// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import "forge-std/Script.sol";
import "../src/RTToken.sol";
import "../src/RTNFT.sol";
import "../src/RTFactory.sol";
import "../src/RTSweeper.sol";

contract DeployRT is Script {
    function run() external {
        uint256 pk = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(pk);
        
        RTToken token = new RTToken();
        RTNFT nft = new RTNFT();
        RTFactory factory = new RTFactory();
        RTSweeper sweeper = new RTSweeper(0xd95F19B25d61f9Fff081bBAc4ff8544e9caA1398);
        
        vm.stopBroadcast();
        
        console.log("RTToken deployed to:", address(token));
        console.log("RTNFT deployed to:", address(nft));
        console.log("RTFactory deployed to:", address(factory));
        console.log("RTSweeper deployed to:", address(sweeper));
    }
}
