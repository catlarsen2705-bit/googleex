// Background service worker for Udsalgstracker extension

// Default settings
const DEFAULT_SETTINGS = {
    backendUrl: 'http://localhost:8000',
    updateInterval: 30,
    notificationsEnabled: true
};

// Store alarm ID
let alarmId = 'udsalgstracker-alarm';

// Load settings
async function getSettings() {
    return new Promise((resolve) => {
        chrome.storage.local.get(DEFAULT_SETTINGS, resolve);
    });
}

// Fetch sales and update badge
async function checkForSales() {
    const settings = await getSettings();

    try {
        const response = await fetch(`${settings.backendUrl}/check-sales`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        // Count stores with sales
        const salesCount = Object.values(data.sales_status || {}).filter(Boolean).length;

        // Update badge
        if (salesCount > 0) {
            chrome.action.setBadgeText({ text: salesCount.toString() });
            chrome.action.setBadgeBackgroundColor({ color: '#fe5370' });

            // Send notification if enabled
            if (settings.notificationsEnabled) {
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'assets/icon-128.png',
                    title: 'Sales found!',
                    message: `${salesCount} store(s) have sales`,
                    priority: 2
                });
            }
        } else {
            chrome.action.setBadgeText({ text: '' });
        }
    } catch (error) {
        console.error('Error checking sales:', error);
        chrome.action.setBadgeText({ text: '!' });
        chrome.action.setBadgeBackgroundColor({ color: '#95a5a6' });
    }
}

// Set up periodic checking
async function setupPeriodicCheck() {
    const settings = await getSettings();
    const intervalMinutes = settings.updateInterval;

    // Clear existing alarm
    chrome.alarms.clear(alarmId);

    // Create new alarm
    chrome.alarms.create(alarmId, {
        periodInMinutes: intervalMinutes
    });

    console.log(`✓ Alarm set to check every ${intervalMinutes} minutes`);

    // Check immediately on startup
    checkForSales();
}

// Listen for alarm
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === alarmId) {
        console.log('Running scheduled sales check...');
        checkForSales();
    }
});

// Listen for storage changes (settings updated)
chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === 'local' && changes.updateInterval) {
        console.log('Update interval changed, resetting alarm...');
        setupPeriodicCheck();
    }
});

// Initialize on install/update
chrome.runtime.onInstalled.addListener(() => {
    console.log('Udsalgstracker extension installed');
    setupPeriodicCheck();
});

// Initialize on startup
setupPeriodicCheck();
