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

    formatScriptMarkdown: (script) => {
        const sections = [
            ['opening', '开头引入'],
            ['material', '材质介绍'],
            ['design', '版型设计'],
            ['details', '细节展示'],
            ['pairing', '搭配建议'],
            ['offer', '促单话术']
        ];

        return sections
            .map(([key, label]) => {
                const rawContent = Array.isArray(script[key]) ? script[key].join('') : (script[key] || '');
                const content = String(rawContent)
                    .replace(/\r\n?/g, '\n')
                    .replace(/\n{3,}/g, '\n\n')
                    .trim();
                return content.trim() ? `## ${label}\n\n${content.trim()}` : '';
            })
            .filter(Boolean)
            .join('\n\n');
    },

    getSectionLabel: (field) => {
        const labels = {
            opening: '开头引入',
            material: '材质介绍',
            design: '版型设计',
            details: '细节展示',
            pairing: '搭配建议',
            offer: '促单话术'
        };
        return labels[field] || field;
    },

    createEmptyScript: () => ({
        opening: [],
        material: [],
        design: [],
        details: [],
        pairing: [],
        offer: []
    })
};
