/* ========================================
   极简高级风格 - JavaScript
   ======================================== */

// Example data
const examples = {
    1: {
        name: '美白精华液',
        info: '主打美白提亮，28天见效',
        comments: [
            '用了皮肤确实变白了',
            '就是价格有点贵',
            '包装很高大上',
            '用了一周效果不明显',
            '会回购的'
        ]
    },
    2: {
        name: '无线蓝牙耳机',
        info: '降噪功能，续航30小时',
        comments: [
            '音质真的很不错',
            '电池续航一般般',
            '操作很简单',
            '比实体店便宜',
            '售后态度很好'
        ]
    },
    3: {
        name: '零食大礼包',
        info: '多种口味，休闲零食组合',
        comments: [
            '味道超级好吃',
            '保质期太短了',
            '回购第三次了',
            '物流有点慢',
            '性价比很高'
        ]
    },
    4: {
        name: '纯棉T恤',
        info: '100%纯棉，舒适透气',
        comments: [
            '穿起来很舒服',
            '尺码偏小',
            '款式好看',
            '质量一般',
            '客服很耐心'
        ]
    }
};

// Load example
function loadExample(type) {
    const example = examples[type];
    if (example) {
        document.getElementById('product-name').value = example.name;
        document.getElementById('product-info').value = example.info;
        document.getElementById('comments').value = example.comments.join('\n');
    }
}

// Generate test comments using simple AI simulation
function generateTestComments() {
    const productName = document.getElementById('product-name').value.trim();
    const productInfo = document.getElementById('product-info').value.trim();

    if (!productName) {
        alert('请先输入商品名称');
        return;
    }

    // Simulated AI-generated comments
    const testComments = [
        `用了效果很好`,
        `质量不错，会推荐给朋友`,
        `比想象中的好一点`,
        `发货很快，包装完好`,
        `客服态度很专业`,
        `性价比可以`,
        `用了一段时间再来评价`,
        `总体满意`
    ];

    // Randomly select 5 comments
    const shuffled = testComments.sort(() => 0.5 - Math.random());
    const selected = shuffled.slice(0, 5);

    document.getElementById('comments').value = selected.join('\n');
}

// Escape HTML
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
        .replace(/\n/g, '\\n');
}

// Merge script parts
function mergeScript(script) {
    return [
        script.opening_hook,
        script.pain_point,
        script.solution,
        script.proof,
        script.offer
    ].join('\n\n');
}

// Copy text
async function copyText(btn, text) {
    try {
        await navigator.clipboard.writeText(text);
        const originalText = btn.textContent;
        btn.textContent = '已复制';
        btn.classList.add('copied');
        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('copied');
        }, 2000);
    } catch (err) {
        console.error('复制失败:', err);
    }
}

// Export scripts
async function exportScripts(format) {
    if (!window.latestResult) {
        alert('请先生成脚本');
        return;
    }

    const btn = format === 'txt'
        ? document.getElementById('export-txt-btn')
        : document.getElementById('export-md-btn');

    const originalText = btn.textContent;
    btn.textContent = '导出中...';
    btn.disabled = true;

    try {
        const { best_script, scripts } = window.latestResult;

        const response = await fetch('/api/export-scripts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                best_script: best_script,
                scripts: scripts || [],
                format: format
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || '导出失败');
        }

        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `直播话术_${new Date().getTime()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        btn.textContent = '已导出';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
        }, 2000);
    } catch (err) {
        console.error('导出失败:', err);
        alert('导出失败: ' + err.message);
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Generate scripts
async function generateScripts() {
    const commentsText = document.getElementById('comments').value;
    const btn = document.getElementById('generate-btn');
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');
    const resultsContent = document.getElementById('results-content');

    // Validate
    const comments = commentsText.split('\n').map(c => c.trim()).filter(c => c);

    if (comments.length === 0) {
        errorEl.textContent = '请输入评论内容';
        errorEl.style.display = 'block';
        resultsContent.style.display = 'none';
        return;
    }

    // Show loading
    btn.disabled = true;
    btn.textContent = '生成中...';
    loadingEl.style.display = 'block';
    errorEl.style.display = 'none';
    resultsContent.style.display = 'none';

    try {
        const response = await fetch('/api/generate-multi-style-scripts-from-comments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comments: comments })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || '请求失败');
        }

        // Store result
        window.latestResult = data;

        // Render
        renderResults(data);

    } catch (error) {
        console.error('Error:', error);
        errorEl.textContent = '生成失败: ' + error.message;
        errorEl.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = '生成脚本';
    }
}

// Render results
function renderResults(data) {
    const loadingEl = document.getElementById('loading');
    const resultsContent = document.getElementById('results-content');

    loadingEl.style.display = 'none';
    resultsContent.style.display = 'block';

    const bestScript = data.best_script;
    const scripts = data.scripts || [];

    let html = '';

    // Recommended card
    if (bestScript) {
        html += `
            <div class="recommended-card">
                <div class="recommended-header">
                    <div class="recommended-title">
                        <h3>推荐脚本</h3>
                        <span class="recommended-tag">${bestScript.style} · ${bestScript.score}分</span>
                    </div>
                    <div class="recommended-actions">
                        <button id="export-txt-btn" class="btn-secondary" onclick="exportScripts('txt')">导出 TXT</button>
                        <button id="export-md-btn" class="btn-secondary" onclick="exportScripts('md')">导出 MD</button>
                    </div>
                </div>
                <div class="recommended-content">
                    <div class="script-part">
                        <div class="script-part-header">
                            <span class="script-part-label"><span class="icon">💬</span>开头吸引</span>
                            <button class="copy-btn" onclick="copyText(this, '${escapeHtml(bestScript.opening_hook)}')">复制</button>
                        </div>
                        <div class="script-part-content">${bestScript.opening_hook}</div>
                    </div>
                    <div class="script-part">
                        <div class="script-part-header">
                            <span class="script-part-label"><span class="icon">🤔</span>痛点描述</span>
                            <button class="copy-btn" onclick="copyText(this, '${escapeHtml(bestScript.pain_point)}')">复制</button>
                        </div>
                        <div class="script-part-content">${bestScript.pain_point}</div>
                    </div>
                    <div class="script-part">
                        <div class="script-part-header">
                            <span class="script-part-label"><span class="icon">✨</span>解决方案</span>
                            <button class="copy-btn" onclick="copyText(this, '${escapeHtml(bestScript.solution)}')">复制</button>
                        </div>
                        <div class="script-part-content">${bestScript.solution}</div>
                    </div>
                    <div class="script-part">
                        <div class="script-part-header">
                            <span class="script-part-label"><span class="icon">📊</span>证明案例</span>
                            <button class="copy-btn" onclick="copyText(this, '${escapeHtml(bestScript.proof)}')">复制</button>
                        </div>
                        <div class="script-part-content">${bestScript.proof}</div>
                    </div>
                    <div class="script-part">
                        <div class="script-part-header">
                            <span class="script-part-label"><span class="icon">🎯</span>促单话术</span>
                            <button class="copy-btn" onclick="copyText(this, '${escapeHtml(bestScript.offer)}')">复制</button>
                        </div>
                        <div class="script-part-content">${bestScript.offer}</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Other scripts
    if (scripts.length > 0) {
        html += '<h3 class="other-scripts-title">其他风格</h3>';
        html += '<div class="scripts-grid">';

        scripts.forEach((script, index) => {
            const styleClass = getStyleClass(script.style);
            const isBest = bestScript && script.style === bestScript.style;

            if (isBest) return;

            html += `
                <div class="script-card ${styleClass}">
                    <div class="script-card-header">
                        <div class="script-card-title">
                            <span class="style-name">${script.style}</span>
                            <span class="score-badge">${script.score || 0}分</span>
                        </div>
                    </div>
                    <div class="script-card-content">
                        <div class="script-card-part">
                            <div class="script-card-part-label">开头吸引</div>
                            <div class="script-card-part-content">${script.opening_hook}</div>
                        </div>
                        <div class="script-card-part">
                            <div class="script-card-part-label">痛点</div>
                            <div class="script-card-part-content">${script.pain_point}</div>
                        </div>
                        <div class="script-card-part">
                            <div class="script-card-part-label">促单</div>
                            <div class="script-card-part-content">${script.offer}</div>
                        </div>
                    </div>
                    <div class="script-card-footer">
                        <button class="btn-secondary" style="width:100%" onclick="copyFullScript(this, ${index})">复制完整话术</button>
                    </div>
                </div>
            `;
        });

        html += '</div>';
    }

    resultsContent.innerHTML = html;

    // Scroll to results
    resultsContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Get style class
function getStyleClass(style) {
    const map = {
        '带货型': 'daihuo',
        '共情型': 'gongqing',
        '理性型': 'lixing'
    };
    return map[style] || 'daihuo';
}

// Copy full script
async function copyFullScript(btn, index) {
    const script = window.latestResult?.scripts?.[index];
    if (!script) return;

    const fullScript = mergeScript(script);
    try {
        await navigator.clipboard.writeText(fullScript);
        const originalText = btn.textContent;
        btn.textContent = '已复制';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    } catch (err) {
        console.error('复制失败:', err);
    }
}
