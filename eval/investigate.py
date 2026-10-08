import sys, os, asyncio, json
sys.path.insert(0, os.path.abspath('backend'))
from aegis.chain.rpc import RpcClient, CuBudget
from aegis.util.ratelimit import TokenBucket
from aegis.chain.effects import effects_from_logs
from aegis.detect.features import get_token_price_and_decimals

hashes = [
"0xa5fe9d044e4f3e5aa5bc4c0709333cd2190cba0f4e7f16bcf73f49f83e4a5460",
"0x27981c7289c372e601c9475e5b5466310be18ed10b59d1ac840145f6e7804c97",
"0xd31b155e259a403ebe69831fae0ec2b4bd33dfa090c43b605a57d5c72c4fbbc7",
"0x4d5201dd4a377f20e61fb8f42e6f929ec16bcec918f0584e39241d15b254a80f",
"0x37a8f4cf553c7e354a38e030cd2303478662f4c28b6f60c5cbc42e5e28d270d7",
"0x2aa93a5503933cb34a521cca87053255054e1bbeb626692da330b8948b86f26b",
"0x48164d3adbab78c2cb9876f6e17f88e321097fcd14cadd57556866e4ef3e185d",
"0xfb546fa579ff71412b7a1e95ffac305df18d9a15432b11420c30c744a631f581",
"0xaa02ec9df4979f4354256a2567acdcc932d6c9698cfdf25fb6bf9d83377559c3",
"0x2407554f821412ec6f6d95d143ab01676b63dc7b6c3af7794b22dcc019349f8e",
"0xed14156ed3670a3e9db938f3323d21ddf322c66cff2391ee58373e500dd8c80b",
"0x03a015d0faa5c763ff2c101fc91ab656607f4cbf9846340b0ba2daca82931b99",
"0x46eec2398ce207ee11dfb0144ba0f7a62308299d6fbc3364b2b0c86694258986"
]

from aegis.chain.effects import effects_from_logs
from aegis.detect.features import get_token_price_and_decimals, extract_features
from aegis.models.case import CaseContext

async def main():
    rpc = RpcClient(os.environ['MAINNET_RPC_URL'], CuBudget(0,0), TokenBucket(10, 10))
    for h in hashes:
        receipt = await rpc.call('eth_getTransactionReceipt', [h])
        tx = await rpc.call('eth_getTransactionByHash', [h])
        if not receipt:
            continue
        effects = effects_from_logs(receipt.get('logs', []))
        
        tx_val_str = tx.get("value", "0")
        if isinstance(tx_val_str, str) and tx_val_str.startswith("0x"):
            tx_val = int(tx_val_str, 16)
        else:
            tx_val = int(tx_val_str) if str(tx_val_str).isdigit() else 0
            
        native_eth_amount = tx_val
        token_amounts = {}
        for eff in effects:
            amount_str = eff.get("amount", "0")
            if not str(amount_str).isdigit(): continue
            amount = int(amount_str)
            if eff.get("kind") == "native_transfer":
                native_eth_amount += amount
            elif eff.get("kind") == "erc20_transfer":
                token = eff.get("token", "")
                if token:
                    token_amounts[token] = token_amounts.get(token, 0) + amount
                    
        usd_val = 0.0
        eth_price, _ = get_token_price_and_decimals("eth_price")
        if eth_price == 0.0: eth_price = 2500.0
        usd_val += (native_eth_amount / (10 ** 18)) * eth_price
        for token, amount in token_amounts.items():
            price, decimals = get_token_price_and_decimals(token)
            usd_val += (amount / (10 ** decimals)) * price
            
        print(f"Hash: {h} | USD: {usd_val}")

asyncio.run(main())
