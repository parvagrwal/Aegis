# Aegis Decisive Errors Ledger

This document enumerates every decisive error (False Positive or False Negative) on the eval dataset.

### Case 0xa5ce309047a92177ad43c03f1f13a87339e38c89509cf5564d79775c4456cf92
- **Expected:** malicious
- **Verdict:** benign
- **Score:** None
- **Features Fired:** []

### Case 0xa5fe9d044e4f3e5aa5bc4c0709333cd2190cba0f4e7f16bcf73f49f83e4a5460
- **Expected:** malicious
- **Verdict:** benign
- **Score:** -500
- **Features Fired:** []

### Case 0x37a8f4cf553c7e354a38e030cd2303478662f4c28b6f60c5cbc42e5e28d270d7
- **Expected:** malicious
- **Verdict:** benign
- **Score:** -500
- **Features Fired:** ['sim.price_unavailable']

### Case 0x2aa93a5503933cb34a521cca87053255054e1bbeb626692da330b8948b86f26b
- **Expected:** malicious
- **Verdict:** benign
- **Score:** -500
- **Features Fired:** ['sim.price_unavailable']

### Case 0x86d68e554304b3ac068ed0780e91715b43e6f4ea46353e1b9634f538888e3257
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 4000
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'sim.large_value_transfer']

### Case 0x6eb15694fe18eff21a092c6b7a9b8259c3a3b6d37d523a05b2b9a6fd2fb6f7d1
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 5200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'code.sweeper_pattern']

### Case 0xe982c7bada5995cb85d7ebad30fbf4f1ee6534a195f44eacf78724af80bcead3
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2500
- **Features Fired:** ['code.sweeper_pattern', 'sim.price_unavailable']

### Case 0xfce10eb8529b86976c82e74c4d95772cb605af75969397431077c865c779fcb3
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2500
- **Features Fired:** ['code.sweeper_pattern']

### Case 0xb271a90a1f0c5e73efed90a84186314d36dbfe7cd7403a471d00ded34648370e
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 3200
- **Features Fired:** ['code.unverified', 'code.sweeper_pattern', 'sim.price_unavailable']

### Case 0xd984bd92e88b041d41ef1667c109f11f5da821eeb08140eb138da304795cdb4e
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0xcd8982543970728de8ce0de315dd701173cf6556d1cbaf53e13d3ab51f991f12
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 5200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'code.sweeper_pattern', 'sim.price_unavailable']

### Case 0x0e8dc38fe9efc4fa4ed2e2320434bab4828f3a1f91c0f39b991e46a3ed4623b8
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x671225dedc5779ecb45c5dde1873c10ad1bde74c87ff6a81a94ddc2735a63507
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0xb5518cc1bd3622ab6c9a655cab80853d906c57f4e138cff64bb7c23589849874
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 4500
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.sweeper_pattern']

### Case 0x198dbb433b1c4f72e782ef91847d5ab8399c3bb1668109fdc21be15194d9a8b9
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0x81aa62ecc0f059bb98297da16a8e8742244fb481c3c9e4960255abaa86281003
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0x3eb742321519b5c15a0dbd1c44a79d17f01dbdcc825b0f5d9a1dac4125eea07b
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x2ee77ad3eeba204520ca60d292c249d30cfa6be54715b2bf6c5bec75fbc5b897
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x71352e7a697b2a64f7a38d4971c74f0b443a2c2010d1b97ec34bf5f658eec80a
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x487a76da306c72ed2d978219d658e021a9a8db138f06ae59a0b29724a9bc6996
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 5200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'code.sweeper_pattern']

### Case 0x9a24173d07b33967ca66b86185aa8e8484b591ad88deafa0b5e5aef9e4dd6477
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x597f51e214bb6ede3cec19d4a630d8b9e567ecd69ff5435322162ab4c30cff8c
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x4339c0912e047509046fdc1edaefeaf78bfdc8ef5effdaa050c9fc04ac60fce3
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x84898bcb94d3d22006d48db4a02f0c6f6ddd8a5a5ada1f8a09c6d3dff305f3c2
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0xa14fa3bc2a81bc7897a345eee2dabcd841ab796112c644c999f90412388056b4
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

