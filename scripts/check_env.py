import os
import sys

required_vars = [
    "AEGIS_ENV", "ALCHEMY_API_KEY", "HELIUS_API_KEY", "ETHERSCAN_API_KEY", 
    "TG_HOST", "TG_GRAPH", "TG_SECRET", "GROQ_API_KEY", "GEMINI_API_KEY", 
    "SIM_PATH", "ATTESTER_PRIVATE_KEY", "ATTESTOR_CONTRACT", 
    "ATTESTOR_DEPLOY_BLOCK", "GUARDIAN_KEYS_JSON", "SOLANA_DEVNET_SECRET", 
    "ANALYST_TOKEN", "OPERATOR_TOKEN", "CORS_ORIGINS"
]

def main():
    missing = []
    # Try to read .env if it exists
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip()
                        if val:  # Only count it if the value is non-empty
                            os.environ[key] = val

    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)

    if missing:
        print("FAIL: The following environment variables are missing or empty:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    
    print("PASS: Environment looks green. All required variables are set.")
    sys.exit(0)

if __name__ == "__main__":
    main()
