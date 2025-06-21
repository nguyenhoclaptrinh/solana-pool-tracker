// static/script.js
let socket;
let updateInterval;
let lastUpdateTime = null;
let lastPools = [];

document.addEventListener('DOMContentLoaded', function() {
    const cachedPools = localStorage.getItem('pools');
    if (cachedPools) {
        updatePoolsTableDisplay(JSON.parse(cachedPools));
    }

    initializeEventListeners();
    socket = io();
    socket.on('connect', () => {
        console.log('Connected to SocketIO server');
        refreshPools();
    });
    socket.on('pools_updated', (data) => {
        console.log('Pools updated for DEX:', data.dex, 'Total pools:', data.pools.length);
        updatePoolsTableDisplay(data.pools);
        localStorage.setItem('pools', JSON.stringify(data.pools));
        lastUpdateTime = new Date().toISOString();
        updateLastUpdateTime();
    });
    socket.on('connect_error', () => {
        console.log('SocketIO connection failed, falling back to polling');
        updateInterval = setInterval(refreshPools, 5000);
    });
});

function initializeEventListeners() {
    const tokenForm = document.getElementById('tokenForm');
    if (tokenForm) {
        tokenForm.addEventListener('submit', handleTokenUpdate);
    }

    const quickAddButtons = document.querySelectorAll('.quick-add');
    quickAddButtons.forEach(button => {
        button.addEventListener('click', handleQuickAdd);
    });

    const refreshPoolsBtn = document.getElementById('refreshPools');
    if (refreshPoolsBtn) {
        refreshPoolsBtn.addEventListener('click', refreshPools);
    }

    const dexFilter = document.getElementById('dexFilter');
    const tokenFilter = document.getElementById('tokenFilter');
    const clearFiltersBtn = document.getElementById('clearFilters');

    if (dexFilter) dexFilter.addEventListener('change', applyFilters);
    if (tokenFilter) tokenFilter.addEventListener('input', debounce(applyFilters, 300));
    if (clearFiltersBtn) clearFiltersBtn.addEventListener('click', clearFilters);
}

function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

async function handleTokenUpdate(e) {
    e.preventDefault();
    const tokenInput = document.getElementById('tokenInput');
    const tokens = tokenInput.value.trim();
    
    if (!tokens) {
        showNotification('Please enter token addresses', 'error');
        return;
    }
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/add-tokens', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `tokens=${encodeURIComponent(tokens)}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification(data.message, 'success');
            updateTokenList(data.tokens);
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error updating tokens: ' + error.message, 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

function handleQuickAdd(e) {
    const tokens = e.target.dataset.tokens;
    const tokenInput = document.getElementById('tokenInput');
    tokenInput.value = tokens;
    const form = document.getElementById('tokenForm');
    form.dispatchEvent(new Event('submit'));
}

function updateTokenList(tokens) {
    const tokenList = document.getElementById('tokenList');
    const tokenCount = document.querySelector('h6');
    
    if (tokenCount) {
        tokenCount.textContent = `Current Token Addresses (${tokens.length}/100)`;
    }
    
    if (tokens.length === 0) {
        tokenList.innerHTML = '<p class="text-muted">No token addresses found</p>';
        return;
    }
    
    tokenList.innerHTML = tokens.map(token => `
        <div class="token-item mb-2">
            <small class="text-muted d-block">${token.substring(0, 20)}...</small>
            <span class="badge bg-secondary">${token}</span>
        </div>
    `).join('');
}

async function refreshPools() {
    try {
        const response = await fetch('/api/pools');
        const data = await response.json();
        updatePoolsTableDisplay(data.pools);
        localStorage.setItem('pools', JSON.stringify(data.pools));
        lastUpdateTime = data.last_updated;
        updateLastUpdateTime();
    } catch (error) {
        console.error('Error refreshing pools:', error);
        showNotification('Error refreshing pools', 'error');
    }
}

function updatePoolsTableDisplay(pools) {
    const tbody = document.getElementById('poolsTableBody');
    const poolCount = document.getElementById('total_pools');

    if (poolCount) {
        poolCount.textContent = `${pools.length} pools`;
    }

    if (pools.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-info-circle me-2"></i>
                    No pools found. Add some token addresses to get started!
                </td>
            </tr>
        `;
        lastPools = [];
        return;
    }

    const currentRows = lastPools.map(p => p.pool_address);
    const newRows = pools.map(p => p.pool_address);
    if (JSON.stringify(currentRows) !== JSON.stringify(newRows)) {
        requestAnimationFrame(() => {
            tbody.innerHTML = pools.map(pool => {
                const dexClass = pool.dex === 'Raydium' ? 'success' : 
                                pool.dex === 'Orca' ? 'info' : 'warning';
                return `
                    <tr class="pool-row" data-dex="${pool.dex}" data-tokena="${pool.tokenA.mint}" data-tokenb="${pool.tokenB.mint}" data-pool-address="${pool.pool_address}">
                        <td>
                            <div>
                                <span class="badge bg-primary">${pool.tokenA.symbol}</span>
                                <span class="badge bg-secondary">${pool.tokenB.symbol}</span>
                                <br>
                                <small class="text-muted">${pool.tokenA.mint.substring(0, 8)}... / ${pool.tokenB.mint.substring(0, 8)}...</small>
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-${dexClass}">${pool.dex}</span>
                        </td>
                        <td>
                            <small class="text-muted">${pool.pool_address.substring(0, 20)}...</small>
                        </td>
                        <td>
                            <strong>$${pool.price.toFixed(8)}</strong>
                        </td>
                        <td>
                            <span class="text-success">$${pool.volume_24h ? pool.volume_24h.toLocaleString() : 0}</span>
                        </td>
                        <td>
                            <span class="text-info">$${pool.liquidity_usd ? pool.liquidity_usd.toLocaleString() : 0}</span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="copyToClipboard('${pool.pool_address}')">
                                <i class="fas fa-copy"></i>
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
            applyFilters();
        });
    }
    lastPools = pools;
}

function applyFilters() {
    const dexFilter = document.getElementById('dexFilter').value;
    const tokenFilter = document.getElementById('tokenFilter').value.toLowerCase();
    const rows = document.querySelectorAll('.pool-row');
    
    rows.forEach(row => {
        const dex = row.dataset.dex;
        const tokenA = row.dataset.tokena.toLowerCase();
        const tokenB = row.dataset.tokenb.toLowerCase();
        
        const dexMatch = !dexFilter || dex === dexFilter;
        const tokenMatch = !tokenFilter || tokenA.includes(tokenFilter) || tokenB.includes(tokenFilter);
        
        row.style.display = dexMatch && tokenMatch ? '' : 'none';
    });
}

function clearFilters() {
    document.getElementById('dexFilter').value = '';
    document.getElementById('tokenFilter').value = '';
    applyFilters();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Pool address copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Error copying to clipboard', 'error');
    });
}

function showNotification(message, type = 'info') {
    const toast = document.getElementById('notificationToast');
    const toastMessage = document.getElementById('toast-message');
    
    if (toast && toastMessage) {
        toastMessage.textContent = message;
        const toastElement = toast.querySelector('.toast');
        toastElement.className = `toast bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} text-white`;
        const bsToast = new bootstrap.Toast(toastElement);
        bsToast.show();
    }
}

function updateLastUpdateTime() {
    if (lastUpdateTime) {
        const now = new Date();
        const lastUpdate = new Date(lastUpdateTime);
        const diffSeconds = Math.floor((now - lastUpdate) / 1000);
        
        let timeText;
        if (diffSeconds < 60) {
            timeText = `${diffSeconds}s ago`;
        } else if (diffSeconds < 3600) {
            timeText = `${Math.floor(diffSeconds / 60)}m ago`;
        } else {
            timeText = `${Math.floor(diffSeconds / 3600)}h ago`;
        }
        
        const lastUpdateElement = document.getElementById('lastUpdate');
        if (lastUpdateElement) {
            lastUpdateElement.innerHTML = `<i class="fas fa-clock me-1"></i>${timeText}`;
        }
    }
}

function stopRealTimeUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    if (socket) {
        socket.disconnect();
    }
}

window.addEventListener('beforeunload', stopRealTimeUpdates);