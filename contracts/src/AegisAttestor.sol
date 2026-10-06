// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

contract AegisAttestor {
    address public immutable attester;
    bytes32 public head;
    uint64 public count;

    event Attested(bytes32 indexed caseKey, uint32 indexed version, bytes32 recordHash,
                   uint8 verdict, uint16 confidenceBps, bytes32 newHead, uint64 seq);
    error NotAttester();
    error LengthMismatch();

    constructor(address attester_) { attester = attester_; }

    function attest(bytes32[] calldata caseKeys, uint32[] calldata versions, bytes32[] calldata recordHashes,
                    uint8[] calldata verdicts, uint16[] calldata confidenceBps) external {
        if (msg.sender != attester) revert NotAttester();
        uint256 n = caseKeys.length;
        if (versions.length != n || recordHashes.length != n || verdicts.length != n || confidenceBps.length != n)
            revert LengthMismatch();
        bytes32 h = head; uint64 c = count;
        for (uint256 i = 0; i < n; ++i) {
            h = keccak256(abi.encodePacked(h, caseKeys[i], versions[i], recordHashes[i]));
            c += 1;
            emit Attested(caseKeys[i], versions[i], recordHashes[i], verdicts[i], confidenceBps[i], h, c);
        }
        head = h; count = c;
    }
}
