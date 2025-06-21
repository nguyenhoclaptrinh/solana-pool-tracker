import requests

def get_all_raydium_pools_by_token_mint(token_mint):
    url = "https://api-v3.raydium.io/pools/info/mint"
    page = 1
    all_pools = []

    while True:
        params = {
            "mint2": "So11111111111111111111111111111111111111112",
            "mint1": token_mint,
            "poolType": "all",
            "poolSortField": "default",
            "sortType": "desc",
            "pageSize": 1000,
            "page": page
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        pools = data.get("data", []).get("data", [])
        if not pools:
            break
        all_pools.extend(pools)
        page += 1

    return all_pools

def simplified_pools(pools):
    simplified_list = [] 
    for pool in pools:
        output = {
            "dex": "Raydium",
            "tokenA": {
                "symbol": pool.get("mintA", {}).get("symbol", "").strip(),
                "mint": pool.get("mintA", {}).get("address", "")
            },
            "tokenB": {
                "symbol": pool.get("mintB", {}).get("symbol", "").strip(),
                "mint": pool.get("mintB", {}).get("address", "")
            },
            "pool_address": pool.get("id", ""),
            "price": pool.get("price", 0),
            "volume_24h": round(pool.get("day", {}).get("volumeQuote", 0), 2),
            "liquidity_usd": round(pool.get("tvl", 0), 2)
        }
        simplified_list.append(output) 
    return simplified_list 

def get_raydium_pools(token_list):
    result = []
    for token in token_list:
        relevant_pools_raw = get_all_raydium_pools_by_token_mint(token)
        simplified_relevant_pools = simplified_pools(relevant_pools_raw)
        result.append(simplified_relevant_pools) 
    return result
