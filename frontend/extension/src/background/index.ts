// Background Service Worker
chrome.runtime.onInstalled.addListener(() => {
    console.log("Virtual Wardrobe Extension Installed");
});

// Example of handling messages from content script if needed
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'SAVE_PRODUCT') {
        // Here you would make a fetch call to your backend API
        // fetch('http://localhost:8000/api/v1/scraper/save', ...)
        console.log("Saving product:", request.payload);
        sendResponse({ status: 'success' });
    }
    return true; // Keep channel open for async response
});

