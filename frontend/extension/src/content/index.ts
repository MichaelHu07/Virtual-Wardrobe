interface ProductMetadata {
    title: string;
    image: string;
    price?: string;
    url: string;
}

const extractMetadata = (): ProductMetadata => {
    // Basic heuristics for product extraction
    const ogTitle = document.querySelector('meta[property="og:title"]')?.getAttribute('content');
    const ogImage = document.querySelector('meta[property="og:image"]')?.getAttribute('content');
    const title = document.title;
    
    // Find largest image if no OG image
    let image = ogImage || '';
    if (!image) {
        const images = Array.from(document.images);
        if (images.length > 0) {
            // Sort by size (area)
            images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
            image = images[0].src;
        }
    }

    return {
        title: ogTitle || title,
        image: image,
        url: window.location.href
    };
};

// Listen for messages from Popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'EXTRACT_PRODUCT') {
        const data = extractMetadata();
        sendResponse(data);
    }
});

