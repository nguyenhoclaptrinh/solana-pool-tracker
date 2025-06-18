# pool_fetcher/raydium.py
import requests

def get_raydium_pools(token_list):
    try:
        res = requests.get("https://api.raydium.io/pairs")
        data = res.json()
        result = []
        for pool in data:
            if pool['baseMint'] in token_list or pool['quoteMint'] in token_list:
                result.append({
                    "dex": "Raydium",
                    "token": pool['name'],
                    "pool_address": pool.get('lpMint'),
                    "price": pool.get('price', 0),
                    "volume": pool.get('volume', 0)
                })
        return result
    except Exception as e:
        print("Raydium Error:", e)
        return []
