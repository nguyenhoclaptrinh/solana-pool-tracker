# app.py
from flask import Flask, render_template, request, jsonify
import json
from pool_fetcher.raydium import get_raydium_pools
from pool_fetcher.orca import get_orca_pools
from pool_fetcher.meteora import get_meteora_pools

app = Flask(__name__)

TOKENS_FILE = "data/tokens.json"
POOLS_FILE = "data/pools.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-token', methods=['POST'])
def add_token():
    new_token = request.json
    with open(TOKENS_FILE, 'r+') as f:
        tokens = json.load(f)
        tokens.append(new_token)
        f.seek(0)
        json.dump(tokens, f, indent=2)
    return {'message': 'Token added'}, 200

@app.route('/api/pools')
def get_pools():
    with open(TOKENS_FILE) as f:
        tokens = json.load(f)
    token_list = [t["mint"] for t in tokens]
    pools = (
        get_raydium_pools(token_list)
        + get_orca_pools(token_list)
        + get_meteora_pools(token_list)
    )
    with open(POOLS_FILE, 'w') as f:
        json.dump(pools, f, indent=2)
    return jsonify(pools)

if __name__ == '__main__':
    app.run(debug=True)
