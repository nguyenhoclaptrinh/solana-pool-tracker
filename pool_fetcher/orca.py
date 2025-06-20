# pool_fetcher/orca.py
import json
import requests


# CONSTAINS
ORCA_API_URL = "https://api.orca.so/v2/solana/pools"


def get_orca_pools(token_list):
    try:
        res = requests.get(ORCA_API_URL)
        pools = res.json().get("data", [])

        result = []
        for pool in pools:
            mint_a = pool.get("tokenMintA")
            mint_b = pool.get("tokenMintB")

            if mint_a in token_list or mint_b in token_list:
                item = {
                    "dex": "Orca",
                    "tokenA": {
                        "symbol": pool["tokenA"]["symbol"],
                        "mint": pool["tokenMintA"]
                    },
                    "tokenB": {
                        "symbol": pool["tokenB"]["symbol"],
                        "mint": pool["tokenMintB"]
                    },
                    "pool_address": pool["address"],
                    "price": float(pool.get("price", 0)),
                    "volume_24h": float(pool.get("stats", {}).get("24h", {}).get("volume", 0)),
                    "liquidity_usd": float(pool.get("tvlUsdc", 0))
                }
                result.append(item)

        # Ghi kết quả vào file orca.json
        # with open("orca_test.json", "w", encoding="utf-8") as f:
        #     json.dump(result, f, ensure_ascii=False, indent=2)

        return result
    except Exception as e:
        print("Orca Error:", e)
        return []


# if __name__ == '__main__':
#     print("Find pool SOL")
#     tokens = ["So11111111111111111111111111111111111111112"]
#     result = get_orca_pools(tokens)
#     print("Done")
