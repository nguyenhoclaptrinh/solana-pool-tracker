# pool_fetcher/meteora.py
import requests

def get_meteora_pools(token_list):
    try:
        res = requests.get("https://api.meteora.ag/pools")  # ví dụ giả định
        data = res.json()
        result = []
        for pool in data['pools']:
            if pool['tokenA']['mint'] in token_list or pool['tokenB']['mint'] in token_list:
                result.append({
                    "dex": "Meteora",
                    "token": pool['tokenA']['symbol'],
                    "pool_address": pool.get('address'),
                    "price": pool.get('price', 0),
                    "volume": pool.get('volumeUSD', 0)
                })
        return result
    except Exception as e:
        print("Meteora Error:", e)
        return []
