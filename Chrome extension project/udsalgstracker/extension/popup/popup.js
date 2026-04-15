// Default settings
const DEFAULT_SETTINGS = {
    backendUrl: 'http://localhost:8000',
    updateInterval: 30,
    notificationsEnabled: true
};

// Load settings from storage
async function loadSettings() {
    return new Promise((resolve) => {
        chrome.storage.local.get(DEFAULT_SETTINGS, (items) => {
            resolve(items);
        });
    });
}

// Save settings to storage
async function saveSettings(settings) {
    return new Promise((resolve) => {
        chrome.storage.local.set(settings, resolve);
    });
}

// Fetch sales data from backend
async function fetchSalesData(backendUrl) {
    try {
        const url = `${backendUrl}/scrape/all`;
        console.log('Fetching from:', url);
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            console.error('Response status:', response.status, response.statusText);
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        console.log('Fetched data:', data);
        return data;
    } catch (error) {
        console.error('Error fetching sales data:', error);
        return null;
    }
}

// Display sales data in popup
function displaySalesData(data) {
    const container = document.getElementById('salesContainer');
    const noSalesMsg = document.getElementById('noSalesMessage');

    if (!data || !data.products || data.products.length === 0) {
        container.innerHTML = '';
        noSalesMsg.style.display = 'flex';
        return;
    }

    noSalesMsg.style.display = 'none';

    // Group products by store
    const byStore = {};
    data.products.forEach(product => {
        const store = product.store || 'Unknown';
        if (!byStore[store]) byStore[store] = [];
        byStore[store].push(product);
    });

    // Render sales by store
    let html = '';
    Object.entries(byStore).forEach(([store, products]) => {
        html += `<div class="sale-item">
            <div class="store-name">${store}</div>
            <ul class="store-products">`;

        products.slice(0, 5).forEach(product => {
            html += `<li class="product">
                <div class="product-name">${product.name}</div>
                <div class="product-price">${product.price.amount} ${product.price.currency}</div>`;
            if (product.url) {
                html += `<a href="${product.url}" target="_blank" class="product-link">See product</a>`;
            }
            html += `</li>`;
        });

        if (products.length > 5) {
            html += `<li class="product"><em>+${products.length - 5} more</em></li>`;
        }

        html += `</ul></div>`;
    });

    container.innerHTML = html;

    // Update last update time
    const now = new Date().toLocaleTimeString('en-US');
    document.getElementById('lastUpdate').textContent = `Last updated: ${now}`;
}

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
    const settings = await loadSettings();

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', async () => {
        document.getElementById('status').textContent = 'Loading data...';
        const data = await fetchSalesData(settings.backendUrl);
        displaySalesData(data);
        document.getElementById('status').textContent = data ? 'Updated' : 'Error';
    });

    // Settings modal
    const modal = document.getElementById('settingsModal');
    const settingsBtn = document.getElementById('settingsBtn');
    const closeBtn = document.querySelector('.close');
    const settingsForm = document.getElementById('settingsForm');

    settingsBtn.addEventListener('click', () => {
        document.getElementById('backendUrl').value = settings.backendUrl;
        document.getElementById('updateInterval').value = settings.updateInterval;
        document.getElementById('notificationsEnabled').checked = settings.notificationsEnabled;
        modal.style.display = 'flex';
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const newSettings = {
            backendUrl: document.getElementById('backendUrl').value,
            updateInterval: parseInt(document.getElementById('updateInterval').value),
            notificationsEnabled: document.getElementById('notificationsEnabled').checked
        };
        await saveSettings(newSettings);
        modal.style.display = 'none';
        alert('Settings saved!');
    });

    // Load initial data
    document.getElementById('status').textContent = 'Updating...';
    const data = await fetchSalesData(settings.backendUrl);
    displaySalesData(data);
    document.getElementById('status').textContent = data ? 'Updated' : 'Error';
});
