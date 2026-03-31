// ===== API Functions =====

// Export to window for use in other scripts
window.API = {
    // Parse product (non-streaming)
    callParseAPI: async (url) => {
        const response = await fetch('/api/parse-product', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        if (!response.ok) throw new Error('Parse failed');
        return response.json();
    },

    // Parse product (streaming)
    callParseStreamAPI: async (params) => {
        const response = await fetch('/api/parse-product-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        if (!response.ok) throw new Error('Parse failed');
        return response;
    },

    // Generate mock comments using AI
    callGenerateCommentsAPI: async (productName, productInfo) => {
        const response = await fetch('/api/generate-comments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_name: productName || '',
                product_info: productInfo || ''
            })
        });
        if (!response.ok) throw new Error('Generate comments failed');
        return response.json();
    }
};