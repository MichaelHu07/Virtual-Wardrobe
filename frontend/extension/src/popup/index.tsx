import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

const Popup = () => {
    const [product, setProduct] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        // Query active tab and send message to content script
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]?.id) {
                chrome.tabs.sendMessage(tabs[0].id, { type: 'EXTRACT_PRODUCT' }, (response) => {
                    if (response) {
                        setProduct(response);
                    }
                });
            }
        });
    }, []);

    const handleSave = async () => {
        setLoading(true);
        // Send to background script which talks to API
        chrome.runtime.sendMessage({ type: 'SAVE_PRODUCT', payload: product }, (res) => {
            setLoading(false);
            if (res?.status === 'success') {
                setSaved(true);
            }
        });
    };

    if (!product) {
        return <div className="p-4 w-64 text-center">Scanning page...</div>;
    }

    return (
        <div className="p-4 w-80 font-sans">
            <h2 className="text-lg font-bold mb-2 text-indigo-600">Virtual Wardrobe</h2>
            
            <div className="mb-4">
                <img src={product.image} alt="Product" className="w-full h-40 object-cover rounded-md mb-2" />
                <h3 className="font-medium text-sm line-clamp-2">{product.title}</h3>
            </div>

            {saved ? (
                <div className="bg-green-100 text-green-700 p-2 rounded text-center text-sm">
                    Saved to Wardrobe!
                </div>
            ) : (
                <button 
                    onClick={handleSave}
                    disabled={loading}
                    className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition disabled:opacity-50"
                >
                    {loading ? 'Saving...' : 'Add to Wardrobe'}
                </button>
            )}
        </div>
    );
};

const root = createRoot(document.getElementById('root')!);
root.render(<Popup />);

