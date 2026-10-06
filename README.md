# AEGIS: Advanced Ethereum Guard Intrusion System

AEGIS is an autonomous intrusion detection and active defense system for EVM networks, built with a robust logic-based policy engine, cryptographic attestations, graph-based pattern matching via TigerGraph, and a natural language (NLP) frontend.

## Features
- **Real-Time Detection:** Strict 4.1s execution window for threat evaluation.
- **Agentic Actions:** Safely queues transaction revocations when malicious actors attempt drainer approval patterns.
- **Cryptographic Attestations:** All case verdicts are perfectly serialized and anchored to the `AegisAttestor` smart contract on Sepolia, guaranteeing tamper-proof logs.
- **Episodic Vector Memory & Graph:** Utilizes TigerGraph queries and fingerprints to track attacker infrastructure over hops, clustering similar attacks effortlessly.
- **Solana Devnet:** Built-in Solana SPL logic checks.

## Setup
```bash
pip install -r backend/requirements.lock.txt
```

## Running
```bash
# Start the Backend
uvicorn backend.aegis.main:app --port 8000
```

## Evaluation Results
The system achieved a perfect 30/30 (100% accuracy) on the final evaluation set (frozen `v1` policy). Check `eval/results/final/metrics.json` for full ablations.