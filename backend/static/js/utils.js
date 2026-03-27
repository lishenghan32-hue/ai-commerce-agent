// ===== Utility Functions =====

// Export to window for use in other scripts
window.Utils = {
    sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),
    generateId: () => Math.random().toString(36).substr(2, 9),

    formatScriptData: (script) => {
        const formatted = {};
        Object.keys(script).forEach(key => {
            formatted[key] = script[key].join('').replace(/。/g, '。\n');
        });
        return formatted;
    },

    getSectionLabel: (field) => {
        const labels = {
            opening_hook: '开头吸引',
            pain_point: '痛点描述',
            solution: '解决方案',
            proof: '证明案例',
            offer: '促单话术'
        };
        return labels[field] || field;
    },

    createEmptyScript: () => ({
        opening_hook: [],
        pain_point: [],
        solution: [],
        proof: [],
        offer: []
    })
};