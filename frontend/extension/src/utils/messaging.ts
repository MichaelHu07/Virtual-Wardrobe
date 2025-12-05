// Utils for messaging between content script, popup, and background
export const sendMessageToBackground = (type: string, payload: any) => {
    return new Promise((resolve) => {
        chrome.runtime.sendMessage({ type, payload }, (response) => {
            resolve(response);
        });
    });
};

