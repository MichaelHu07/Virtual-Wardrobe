// Background Service Worker
chrome.runtime.onInstalled.addListener(() => {
    console.log("Virtual Wardrobe Extension Installed");
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'SAVE_PRODUCT') {
        // Send to Backend API
        fetch('http://localhost:8000/api/v1/scraper/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request.payload)
        })
        .then(response => response.json())
        .then(data => {
            console.log("Product saved:", data);
            sendResponse({ status: 'success', data });
        })
        .catch(error => {
            console.error("Save failed:", error);
            sendResponse({ status: 'error', error: error.message });
        });
        
        return true; // Keep channel open for async response
    }
});
