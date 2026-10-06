import os
from pathlib import Path

repo_root = Path("C:/Users/parva/OneDrive/Desktop/HHGoa- Aegis")

directories = [
    "docs/perf",
    "contracts/src",
    "contracts/test",
    "redteam/contracts/src",
    "backend/config",
    "backend/aegis/util",
    "backend/aegis/models",
    "backend/aegis/chain",
    "backend/aegis/intel/data",
    "backend/aegis/detect",
    "backend/aegis/policy",
    "backend/aegis/graph/gsql",
    "backend/aegis/agent",
    "backend/aegis/defend",
    "backend/aegis/attest",
    "backend/aegis/ingest",
    "backend/aegis/console",
    "backend/aegis/api",
    "backend/aegis/eval",
    "backend/tests",
    "scripts",
    "verify",
    "eval/official",
    "eval/results/final",
    "frontend"
]

files = {
    "README.md": "# AEGIS",
    ".env.example": "",
    ".python-version": "3.13",
    "render.yaml": "",
    "docs/day0-verification.md": "# Day 0 Verification\n",
    "docs/ui-contract.md": "",
    "docs/liveness-log.md": "",
    "contracts/foundry.toml": "",
    "contracts/src/AegisAttestor.sol": "",
    "contracts/test/AegisAttestor.t.sol": "",
    "redteam/contracts/src/RTToken.sol": "",
    "redteam/contracts/src/RTNFT.sol": "",
    "redteam/contracts/src/RTDrainer.sol": "",
    "redteam/contracts/src/RTFactory.sol": "",
    "redteam/contracts/src/RTSweeper.sol": "",
    "redteam/fire.py": "",
    "redteam/scenarios.json": "[]",
    "backend/.python-version": "3.13",
    "backend/requirements.txt": "",
    "backend/requirements.lock.txt": "",
    "backend/config/chains.json": "{}",
    "backend/config/policy.v1.json": "{}",
    "backend/config/cu_costs.json": "{}",
    "backend/config/prices.static.json": "{}",
    "backend/config/console_grammar.json": "{}",
    "backend/aegis/__init__.py": "",
    "backend/aegis/main.py": "",
    "backend/aegis/config.py": "",
    "verify/verify_attestation.py": "",
    "eval/cases.json": "{}",
    "eval/dev_cases.json": "{}",
    "eval/FREEZE.md": "",
    "eval/CHANGELOG.md": "",
}

for d in directories:
    (repo_root / d).mkdir(parents=True, exist_ok=True)
    
for f, content in files.items():
    file_path = repo_root / f
    if not file_path.exists():
        file_path.write_text(content, encoding="utf-8")

scripts = [
    "check_env.py", "probe_sim.py", "probe_ws.py", "fetch_intel.py", "verify_allowlist.py",
    "audit_cases.py", "tg_setup.py", "mic_test.html", "check_secrets.py"
]
for s in scripts:
    (repo_root / "scripts" / s).touch()

modules = {
    "util": ["canonical.py", "ids.py", "timing.py", "ratelimit.py", "logging.py"],
    "models": ["events.py", "evidence.py", "case.py", "actions.py", "attest.py", "api.py"],
    "chain": ["rpc.py", "budget.py", "explorer.py", "helius.py", "abi_registry.py", "decoder.py", "typed_data.py", "simulate.py", "effects.py", "tokens.py", "prices.py", "bytecode.py"],
    "intel": ["labels.py", "allowlist.py", "goplus.py"],
    "detect": ["triage.py", "roles.py", "profile.py", "features.py", "lookalike.py", "solana_detect.py"],
    "policy": ["engine.py", "rules.py", "calibration.py"],
    "graph": ["tg_client.py", "loader.py", "queries.py", "local_graph.py"],
    "agent": ["orchestrator.py", "planner.py", "tools.py", "permissions.py", "memory.py", "explain.py", "narrator.py", "llm_router.py"],
    "defend": ["actions.py", "queue.py", "executor.py"],
    "attest": ["record.py", "anchor_evm.py", "anchor_sol.py", "verify.py", "store.py"],
    "ingest": ["bus.py", "evm_ws.py", "evm_poll.py", "solana_ws.py", "watchlist.py", "firehose.py"],
    "console": ["grammar.py"],
    "api": ["routes_cases.py", "routes_defend.py", "ws.py", "auth.py", "deps.py"],
    "eval": ["adapter.py", "harness.py", "metrics.py", "report.py", "build_dev_set.py"]
}

for folder, pyfiles in modules.items():
    for pyf in pyfiles:
        (repo_root / "backend" / "aegis" / folder / pyf).touch()

print("Scaffolded repository layout successfully.")
