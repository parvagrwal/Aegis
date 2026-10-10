# Aegis Decisive Errors Ledger

This document enumerates every decisive error (False Positive or False Negative) on the eval dataset.

Generated from harness run at 2026-10-10T12:38:49.404116+00:00 by eval/harness.py.
Uncertain verdicts are honest abstentions, not errors, and are not listed here.

### Case 0xed26708a7335116bdb0673f32ace7c2f329fe3cd349e200447210f1721f335f0 (False Negative)
- **Expected:** malicious
- **Verdict:** benign
- **Score:** 200
- **Risk:** LOW
- **Features Fired:** ['code.unverified']

### Case 0xa5fe9d044e4f3e5aa5bc4c0709333cd2190cba0f4e7f16bcf73f49f83e4a5460 (False Negative)
- **Expected:** malicious
- **Verdict:** benign
- **Score:** -500
- **Risk:** LOW
- **Features Fired:** []

### Case 0x7fe367e61a7680d4b563d05ed82658af8d5a88f98c332d66f087a3db7e6f9097 (False Negative)
- **Expected:** malicious
- **Verdict:** benign
- **Score:** 200
- **Risk:** LOW
- **Features Fired:** ['code.unverified', 'sim.price_unavailable']

### Case 0x37a8f4cf553c7e354a38e030cd2303478662f4c28b6f60c5cbc42e5e28d270d7 (False Negative)
- **Expected:** malicious
- **Verdict:** benign
- **Score:** -500
- **Risk:** LOW
- **Features Fired:** ['sim.price_unavailable']

### Case 0x2aa93a5503933cb34a521cca87053255054e1bbeb626692da330b8948b86f26b (False Negative)
- **Expected:** malicious
- **Verdict:** benign
- **Score:** -500
- **Risk:** LOW
- **Features Fired:** ['sim.price_unavailable']

### Case 0xd984bd92e88b041d41ef1667c109f11f5da821eeb08140eb138da304795cdb4e (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0x7f876fcb6f4391ee58e5c0a31aa027f3ff596c3194d10a615ddee5014d458fb5 (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0x03d92804a7745e33226f3acf5be46d26171ed11b1768d30a8f8b2fc687f0c0ae (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0x8803fa2b68f25be9029222c460df91c33a8f9f7ac3bddbb5cb1ab0f6b35d3e32 (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x17080b5c0a3ee9dde7163db93084e49b6da6cbd140c3626b0aeeec200c07f9aa (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0xc76bb2534c74e8d6260da162504d1f44a800ae109ec7d2a0a70338b61e0783fb (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x671225dedc5779ecb45c5dde1873c10ad1bde74c87ff6a81a94ddc2735a63507 (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0x198dbb433b1c4f72e782ef91847d5ab8399c3bb1668109fdc21be15194d9a8b9 (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0xb9429db946c8dda31a562ea871526eddc2904821a92725a1f8c004918fa9bc68 (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0x683d0fe79b3c8fb1c62e3e8dccbe123510286e623dc3dbea48f7e6eba9ae0242 (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified', 'sim.price_unavailable']

### Case 0xbef94cc7d47dbe68578ab01d137024c997e40e14dfff70802426c4a58166af95 (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0xf55b0e61564c35d8834dbb9b62301c25f942c1aa102cf76aa1ecd80d76d5447e (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0xd213d6a83475f10caa3acb75584d6a1fc5a276d79649b23bc9978881f6d1d73c (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']

### Case 0x2b1e0acd7538bd693f7330f604b7293715446892611818f9fa0acf8df7d5270a (False Positive)
- **Expected:** benign
- **Verdict:** malicious
- **Score:** 2200
- **Risk:** HIGH
- **Features Fired:** ['sim.subject_outflow_no_inflow', 'code.unverified']
