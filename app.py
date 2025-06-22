from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import threading
import time
from flask_socketio import SocketIO
from pool_fetcher.raydium import get_raydium_pools
from pool_fetcher.orca import get_orca_pools
from pool_fetcher.meteora import get_meteora_pools

app = Flask(__name__)
socketio = SocketIO(app)

TOKENS_FILE = 'data/tokens.txt'
POOLS_RAYDIUM_FILE = 'data/pools_raydium.json'
POOLS_ORCA_FILE = 'data/pools_orca.json'
POOLS_METEORA_FILE = 'data/pools_meteora.json'
UPDATE_INTERVAL = 5
update_flag = threading.Event()

raydium_lock = threading.Lock()
orca_lock = threading.Lock()
meteora_lock = threading.Lock()

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            tokens = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            return tokens
    return []

def save_tokens(tokens):
    os.makedirs('data', exist_ok=True)
    with open(TOKENS_FILE, 'w') as f:
        for token in tokens:
            f.write(f"{token}\n")

def save_pools_file(pools, fname):
    os.makedirs('data', exist_ok=True)
    with open(fname, 'w') as f:
        json.dump(pools, f, indent=2)

def update_raydium_pools(tokens):
    if not raydium_lock.acquire(blocking=False):
        print("[SKIP] Raydium update is already running, skipping this cycle.")
        return
    try:
        print(f"[UPDATE] Raydium updating at {datetime.now()}")
        pools = get_raydium_pools(tokens) if tokens else []
        save_pools_file(pools, POOLS_RAYDIUM_FILE)
        socketio.emit('pools_updated', {'dex': 'Raydium', 'pools': load_all_pools(), 'last_updated': datetime.now().isoformat()})
        print(f"[UPDATE] Raydium pools updated at {datetime.now()}")
    except Exception as e:
        print(f"[ERROR] Raydium update error: {e}")
    finally:
        raydium_lock.release()

def update_orca_pools(tokens):
    if not orca_lock.acquire(blocking=False):
        print("[SKIP] Orca update is already running, skipping this cycle.")
        return
    try:
        print(f"[UPDATE] Orca updating at {datetime.now()}")
        pools = get_orca_pools(tokens) if tokens else []
        save_pools_file(pools, POOLS_ORCA_FILE)
        socketio.emit('pools_updated', {'dex': 'Orca', 'pools': load_all_pools(), 'last_updated': datetime.now().isoformat()})
        print(f"[UPDATE] Orca pools updated at {datetime.now()}")
    except Exception as e:
        print(f"[ERROR] Orca update error: {e}")
    finally:
        orca_lock.release()

def update_meteora_pools(tokens):
    if not meteora_lock.acquire(blocking=False):
        print("[SKIP] Meteora update is already running, skipping this cycle.")
        return
    try:
        print(f"[UPDATE] Meteora updating at {datetime.now()}")
        pools = get_meteora_pools(tokens) if tokens else []
        save_pools_file(pools, POOLS_METEORA_FILE)
        socketio.emit('pools_updated', {'dex': 'Meteora', 'pools': load_all_pools(), 'last_updated': datetime.now().isoformat()})
        print(f"[UPDATE] Meteora pools updated at {datetime.now()}")
    except Exception as e:
        print(f"[ERROR] Meteora update error: {e}")
    finally:
        meteora_lock.release()

def background_updater():
    print(f"[START] Background updater started at {datetime.now()}")
    while True:
        update_flag.wait()
        tokens = load_tokens()
        if tokens:
            threading.Thread(target=update_raydium_pools, args=(tokens,), daemon=True).start()
            threading.Thread(target=update_orca_pools, args=(tokens,), daemon=True).start()
            threading.Thread(target=update_meteora_pools, args=(tokens,), daemon=True).start()
        else:
            save_pools_file([], POOLS_RAYDIUM_FILE)
            save_pools_file([], POOLS_ORCA_FILE)
            save_pools_file([], POOLS_METEORA_FILE)
            socketio.emit('pools_updated', {'dex': 'All', 'pools': [], 'last_updated': datetime.now().isoformat()})
        update_flag.clear()
        time.sleep(UPDATE_INTERVAL)

def load_all_pools():
    pools = []
    for fname in [POOLS_RAYDIUM_FILE, POOLS_ORCA_FILE, POOLS_METEORA_FILE]:
        if os.path.exists(fname):
            try:
                with open(fname, 'r') as f:
                    pools.extend(json.load(f))
            except Exception as e:
                print(f"[ERROR] Failed to load {fname}: {e}")
    return pools

@app.route('/')
def index():
    tokens = load_tokens()
    pools = load_all_pools()
    return render_template('index.html', tokens=tokens, pools=pools)

@app.route('/add-tokens', methods=['POST'])
def add_tokens():
    token_input = request.form.get('tokens', '').strip()
    print(f"[UPDATE] Adding tokens: {token_input}")
    if not token_input:
        return jsonify({'error': 'Please enter token addresses'}), 400
    tokens = []

    for line in token_input.split('\n'):
        for token in line.split(','):
            token = token.strip()
            if token and token not in tokens:
                tokens.append(token)

    if not tokens:
        return jsonify({'error': 'No valid tokens found'}), 400
    if len(tokens) > 100:
        return jsonify({'error': 'Maximum 100 tokens allowed'}), 400
    save_tokens(tokens)
    update_flag.set()

    return jsonify({
        'success': True,
        'message': f'Updated {len(tokens)} tokens and fetched pools',
        'tokens': tokens
    })

@app.route('/api/pools')
def api_pools():
    pools = load_all_pools()
    return jsonify({
        'pools': pools,
        'last_updated': datetime.now().isoformat(),
        'total_pools': len(pools)
    })

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    with open(TOKENS_FILE, 'w') as f:
        f.write('')
    for fname in [POOLS_RAYDIUM_FILE, POOLS_ORCA_FILE, POOLS_METEORA_FILE]:
        with open(fname, 'w') as f:
            f.write('[]')

    print("[START] Starting Solana Pool Tracker...")
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    print(f"[START] Server starting on http://localhost:5000")
    print(f"[INFO] Auto-update interval: {UPDATE_INTERVAL} seconds")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)