// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import "forge-std/Test.sol";
import "../src/AegisAttestor.sol";

contract AegisAttestorTest is Test {
    AegisAttestor public attestor;
    address public attester = address(0x123);
    address public notAttester = address(0x456);

    function setUp() public {
        attestor = new AegisAttestor(attester);
    }

    function testAttestSingle() public {
        bytes32[] memory caseKeys = new bytes32[](1);
        uint32[] memory versions = new uint32[](1);
        bytes32[] memory recordHashes = new bytes32[](1);
        uint8[] memory verdicts = new uint8[](1);
        uint16[] memory confidenceBps = new uint16[](1);

        caseKeys[0] = keccak256("case1");
        versions[0] = 1;
        recordHashes[0] = keccak256("record1");
        verdicts[0] = 1; // malicious
        confidenceBps[0] = 9500;

        vm.prank(attester);
        attestor.attest(caseKeys, versions, recordHashes, verdicts, confidenceBps);

        assertEq(attestor.count(), 1);
    }

    function testAttestBatch() public {
        bytes32[] memory caseKeys = new bytes32[](2);
        uint32[] memory versions = new uint32[](2);
        bytes32[] memory recordHashes = new bytes32[](2);
        uint8[] memory verdicts = new uint8[](2);
        uint16[] memory confidenceBps = new uint16[](2);

        caseKeys[0] = keccak256("case1");
        versions[0] = 1;
        recordHashes[0] = keccak256("record1");
        verdicts[0] = 1;
        confidenceBps[0] = 9500;

        caseKeys[1] = keccak256("case2");
        versions[1] = 1;
        recordHashes[1] = keccak256("record2");
        verdicts[1] = 2; // benign
        confidenceBps[1] = 9000;

        vm.prank(attester);
        attestor.attest(caseKeys, versions, recordHashes, verdicts, confidenceBps);

        assertEq(attestor.count(), 2);
    }

    function testNonAttesterReverts() public {
        bytes32[] memory caseKeys = new bytes32[](0);
        uint32[] memory versions = new uint32[](0);
        bytes32[] memory recordHashes = new bytes32[](0);
        uint8[] memory verdicts = new uint8[](0);
        uint16[] memory confidenceBps = new uint16[](0);

        vm.prank(notAttester);
        vm.expectRevert(AegisAttestor.NotAttester.selector);
        attestor.attest(caseKeys, versions, recordHashes, verdicts, confidenceBps);
    }

    function testHeadChainMatches() public {
        bytes32[] memory caseKeys = new bytes32[](1);
        uint32[] memory versions = new uint32[](1);
        bytes32[] memory recordHashes = new bytes32[](1);
        uint8[] memory verdicts = new uint8[](1);
        uint16[] memory confidenceBps = new uint16[](1);

        caseKeys[0] = keccak256("case1");
        versions[0] = 1;
        recordHashes[0] = keccak256("record1");
        verdicts[0] = 1;
        confidenceBps[0] = 9500;

        vm.prank(attester);
        attestor.attest(caseKeys, versions, recordHashes, verdicts, confidenceBps);

        bytes32 expectedHead = keccak256(abi.encodePacked(bytes32(0), caseKeys[0], versions[0], recordHashes[0]));
        assertEq(attestor.head(), expectedHead);
    }
}
