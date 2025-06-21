from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException

SOL_MINT = "So11111111111111111111111111111111111111112"

def get_meteora_pools(token_list: Optional[List[str]] = None) -> List[Dict]:
    url = "https://dlmm-api.meteora.ag/pair/all"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        pools_data = response.json()
    except RequestException as e:
        raise RequestException(f"Failed to fetch Meteora pools: {str(e)}")

    results = []
    
    for pool in pools_data:
        mint_x = pool.get("mint_x")
        mint_y = pool.get("mint_y")
        pool_name = pool.get("name", "")
        
        if (mint_x == SOL_MINT and mint_y in token_list) or (mint_x in token_list and mint_y == SOL_MINT):
            if mint_x == SOL_MINT:
                sol_token = {
                    "symbol": "SOL",
                    "mint": SOL_MINT
                }
                other_token = {
                    "symbol": next((s for s in pool_name.split("-") if s != "SOL"), "UNKNOWN"),
                    "mint": mint_y
                }
                price = float(pool.get("current_price", 0))
            else:
                sol_token = {
                    "symbol": "SOL",
                    "mint": SOL_MINT
                }
                other_token = {
                    "symbol": next((s for s in pool_name.split("-") if s != "SOL"), "UNKNOWN"),
                    "mint": mint_x
                }
                price = 1 / float(pool.get("current_price", 1))

            results.append({
                "dex": "Meteora",
                "tokenA": sol_token,
                "tokenB": other_token,
                "pool_address": pool.get("address"),
                "price": price,
                "volume_24h": float(pool.get("trade_volume_24h", 0)),
                "liquidity_usd": float(pool.get("liquidity", 0))
            })
    
    return results

