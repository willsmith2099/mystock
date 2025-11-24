document.addEventListener('DOMContentLoaded', () => {
    // State
    let watchlist = [];
    let charts = {};
    const REFRESH_INTERVAL = 60000; // 1 minute

    // DOM Elements
    const watchlistBody = document.getElementById('watchlist-body');
    const loadingSkeleton = document.getElementById('loading-skeleton');
    const stockSearch = document.getElementById('stock-search');
    const searchResults = document.getElementById('search-results');
    const themeToggle = document.getElementById('theme-toggle');
    const watchlistCount = document.getElementById('watchlist-count');
    const lastUpdate = document.getElementById('last-update');
    const template = document.getElementById('stock-row-template');

    // Theme Handling
    const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark for trading
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update charts theme
        Object.values(charts).forEach(chart => {
            updateChartTheme(chart, newTheme);
        });
    });

    // Initial Load
    fetchWatchlist();
    setInterval(fetchWatchlist, REFRESH_INTERVAL);

    // Search Functionality
    let searchTimeout;
    stockSearch.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();

        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    renderSearchResults(data);
                })
                .catch(err => console.error('Search error:', err));
        }, 300);
    });

    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!stockSearch.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });

    function renderSearchResults(results) {
        searchResults.innerHTML = '';
        if (results.length === 0) {
            searchResults.classList.add('hidden');
            return;
        }

        results.forEach(stock => {
            const div = document.createElement('div');
            div.className = 'search-item';
            div.innerHTML = `
                <span>${stock.name}</span>
                <span style="color: var(--text-secondary)">${stock.ts_code}</span>
            `;
            div.addEventListener('click', () => {
                addToWatchlist(stock.ts_code);
                stockSearch.value = '';
                searchResults.classList.add('hidden');
            });
            searchResults.appendChild(div);
        });
        searchResults.classList.remove('hidden');
    }

    // Watchlist Management
    async function fetchWatchlist() {
        try {
            const res = await fetch('/api/watchlist');
            const data = await res.json();

            // Hide loading skeleton
            if (loadingSkeleton) {
                loadingSkeleton.style.display = 'none';
            }

            // Update stats
            watchlistCount.textContent = data.length;
            lastUpdate.textContent = new Date().toLocaleTimeString();

            const currentCodes = new Set(data.map(s => s.code));

            // Remove rows not in watchlist
            Array.from(watchlistBody.children).forEach(row => {
                if (!currentCodes.has(row.dataset.code)) {
                    row.remove();
                    if (charts[row.dataset.code]) {
                        charts[row.dataset.code].destroy();
                        delete charts[row.dataset.code];
                    }
                }
            });

            // Add or update rows
            data.forEach((stock, index) => {
                let row = watchlistBody.querySelector(`.stock-row[data-code="${stock.code}"]`);
                if (!row) {
                    row = createRow(stock, index + 1);
                    watchlistBody.appendChild(row);
                    // Fetch detailed data for new row
                    fetchStockDetail(stock.code);
                } else {
                    // Update basic info
                    updateRowBasic(row, stock, index + 1);
                }
            });
        } catch (err) {
            console.error('Error fetching watchlist:', err);
            showToast('Failed to update watchlist', 'error');
        }
    }

    function createRow(stock, index) {
        const clone = template.content.cloneNode(true);
        const row = clone.querySelector('.stock-row');
        row.dataset.code = stock.code;

        row.querySelector('.remove-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            removeFromWatchlist(stock.code, stock.name);
        });

        updateRowBasic(row, stock, index);
        return row;
    }

    function updateRowBasic(row, stock, index) {
        row.querySelector('.col-index').textContent = index;
        row.querySelector('.col-code').textContent = stock.code;
        row.querySelector('.col-name').textContent = stock.name || stock.code;

        if (stock.error) {
            row.querySelector('.col-price').textContent = 'Error';
            return;
        }

        const priceEl = row.querySelector('.col-price');
        const pctEl = row.querySelector('.col-pct');
        const changeEl = row.querySelector('.col-change');

        priceEl.textContent = stock.price.toFixed(2);

        const pct = stock.pct_chg.toFixed(2) + '%';
        pctEl.textContent = (stock.pct_chg > 0 ? '+' : '') + pct;

        const change = stock.change.toFixed(2);
        changeEl.textContent = (stock.change > 0 ? '+' : '') + change;

        // Color coding
        const colorClass = stock.change >= 0 ? 'text-up' : 'text-down';
        priceEl.className = `col-price text-right ${colorClass}`;
        pctEl.className = `col-pct text-right ${colorClass}`;
        changeEl.className = `col-change text-right ${colorClass}`;
    }

    async function fetchStockDetail(code) {
        try {
            const res = await fetch(`/api/stock/${code}`);
            if (!res.ok) throw new Error('Failed to fetch details');
            const data = await res.json();

            const row = watchlistBody.querySelector(`.stock-row[data-code="${code}"]`);
            if (!row) return;

            // Update indicators
            const tech = data.technical;
            const inst = data.institutional;

            row.querySelector('.col-rsi').textContent = tech.rsi ? tech.rsi.toFixed(1) : '-';
            row.querySelector('.col-ma5').textContent = tech.ma5 ? tech.ma5.toFixed(2) : '-';

            // Institutional flow
            const flow = inst.main_net_inflow_total;
            const flowEl = row.querySelector('.col-flow');
            if (flow) {
                const flowInWan = (flow / 10000).toFixed(1) + '万';
                flowEl.textContent = flowInWan;
                flowEl.className = `col-flow text-right ${flow > 0 ? 'text-up' : 'text-down'}`;
            } else {
                flowEl.textContent = '-';
            }

            // Render Chart
            renderMiniChart(row, data.history);

        } catch (err) {
            console.error(`Error fetching details for ${code}:`, err);
        }
    }

    function renderMiniChart(row, history) {
        const canvas = row.querySelector('.mini-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const code = row.dataset.code;

        if (charts[code]) {
            charts[code].destroy();
        }

        const prices = history.map(h => h.close).reverse();
        const labels = history.map(h => h.trade_date).reverse();

        const isUp = prices[prices.length - 1] >= prices[0];
        const color = isUp ? '#ef4444' : '#10b981'; // Red Up, Green Down

        charts[code] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: prices,
                    borderColor: color,
                    borderWidth: 1.5,
                    tension: 0.4,
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: {
                    x: { display: false },
                    y: { display: false, min: Math.min(...prices) * 0.99, max: Math.max(...prices) * 1.01 }
                },
                animation: { duration: 0 }
            }
        });
    }

    function updateChartTheme(chart, theme) {
        // For mini charts in table, we might not need to change much on theme switch
        // as the line color depends on price change.
    }

    async function addToWatchlist(code) {
        // Prevent duplicate adds
        if (watchlistBody.querySelector(`.stock-row[data-code="${code}"]`)) {
            showToast('Stock already in watchlist', 'error');
            return;
        }

        showToast(`Adding ${code}...`);

        try {
            const res = await fetch('/api/watchlist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            const data = await res.json();
            if (data.success) {
                showToast(`Added ${code} successfully`);
                // Refresh immediately
                fetchWatchlist();
            } else {
                showToast(data.error || 'Failed to add stock', 'error');
            }
        } catch (err) {
            showToast('Failed to add stock', 'error');
        }
    }

    async function removeFromWatchlist(code, name) {
        const confirmMsg = name ? `Remove ${name} (${code})?` : `Remove ${code}?`;
        if (!confirm(confirmMsg)) return;

        const row = watchlistBody.querySelector(`.stock-row[data-code="${code}"]`);
        if (row) {
            row.style.opacity = '0.5';
        }

        try {
            const res = await fetch(`/api/watchlist/${code}`, {
                method: 'DELETE'
            });
            const data = await res.json();
            if (data.success) {
                showToast(`Removed ${code}`);
                if (row) {
                    row.remove();
                }
                // Update count
                const currentCount = parseInt(watchlistCount.textContent) || 0;
                watchlistCount.textContent = Math.max(0, currentCount - 1);
            } else {
                if (row) row.style.opacity = '1';
                showToast('Failed to remove stock', 'error');
            }
        } catch (err) {
            if (row) row.style.opacity = '1';
            showToast('Failed to remove stock', 'error');
        }
    }

    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        if (type === 'error') toast.style.borderLeft = '4px solid var(--danger-color)';
        else toast.style.borderLeft = '4px solid var(--success-color)';

        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
