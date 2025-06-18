# pool_fetcher/orca.py
import requests
import json


def get_orca_pools(token_list):
    try:
        url = "https://api.orca.so/v2/solana/pools"
        res = requests.get(url)
        pools = res.json().get("data", [])

        # Ghi kết quả vào file orca.json
        with open("orca.json", "w", encoding="utf-8") as f:
            json.dump(pools, f, ensure_ascii=False, indent=2)
        # print(pools)
        result = []
        for pool in pools:
            mint_a = pool.get("tokenMintA")
            mint_b = pool.get("tokenMintB")

            if mint_a in token_list or mint_b in token_list:
                token = pool['tokenA']['symbol'] if mint_a in token_list else pool['tokenB']['symbol']
                result.append({
                    "dex": "Orca",
                    "tokenA": tokenA,
                    "tokenB": tokenB,
                    "price": float(pool.get("price", 0)),
                    "volume": float(pool.get("stats", {}).get("ANY_ADDITIONAL_PROPERTY", {}).get("volume", 0))
                    "pool_address": pool.get("address"),
                })

        return result
    except Exception as e:
        print("Orca Error:", e)
        return []


if __name__ == '__main__':
    print("find pool SOL")
    tokens = ["So11111111111111111111111111111111111111112"]
    result = get_orca_pools(tokens)
