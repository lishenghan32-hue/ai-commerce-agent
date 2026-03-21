/* ========================================
   极简高级风格 - JavaScript
   ======================================== */

// Example data
const examples = {
    1: {
        name: '美白精华液',
        info: '主打美白提亮，28天见效',
        selling_points: '美白提亮，28天见效，温和不刺激',
        comments: ['用了皮肤确实变白了', '就是价格有点贵', '包装很高大上', '用了一周效果不明显', '会回购的']
    },
    2: {
        name: '无线蓝牙耳机',
        info: '降噪功能，续航30小时',
        selling_points: '主动降噪，30小时续航，Hi-Fi音质',
        comments: ['音质真的很不错', '电池续航一般般', '操作很简单', '比实体店便宜', '售后态度很好']
    },
    3: {
        name: '零食大礼包',
        info: '多种口味，休闲零食组合',
        selling_points: '多种口味，独立包装，性价比高',
        comments: ['味道超级好吃', '保质期太短了', '回购第三次了', '物流有点慢', '性价比很高']
    },
    4: {
        name: '纯棉T恤',
        info: '100%纯棉，舒适透气',
        selling_points: '100%纯棉，舒适透气，多色可选',
        comments: ['穿起来很舒服', '尺码偏小', '款式好看', '质量一般', '客服很耐心']
    }
};

// Load example
function loadExample(type) {
    const example = examples[type];
    if (example) {
        document.getElementById('product-name').value = example.name;
        document.getElementById('product-info').value = example.info;
        document.getElementById('selling-points').value = example.selling_points || '';
        document.getElementById('comments').value = example.comments.join('\n');
    }
}

// Generate test comments
function generateTestComments() {
    const productName = document.getElementById('product-name').value.trim();

    if (!productName) {
        alert('请先输入商品名称');
        return;
    }

    const testComments = [
        `用了效果很好`, `质量不错，会推荐给朋友`,
        `比想象中的好一点`, `发货很快，包装完好`,
        `客服态度很专业`, `性价比可以`,
        `用了一段时间再来评价`, `总体满意`
    ];

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
    return [script.opening_hook, script.pain_point, script.solution, script.proof, script.offer].join('\n\n');
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

    if (!btn) return;

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

// Toggle result card
function toggleResultCard(item) {
    item.classList.toggle('expanded');
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

// Update progress steps
function updateProgressStep(stepNum, status) {
    const step = document.getElementById(`step-${stepNum}`);
    if (!step) return;

    step.classList.remove('active', 'completed');
    if (status) {
        step.classList.add(status);
    }
}

// Generate scripts with SSE
async function generateScripts() {
    const productName = document.getElementById('product-name').value.trim();
    const productInfo = document.getElementById('product-info').value.trim();
    const sellingPoints = document.getElementById('selling-points').value.trim();
    const commentsText = document.getElementById('comments').value;
    const btn = document.getElementById('generate-btn');
    const emptyState = document.getElementById('empty-state');
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');
    const resultsContent = document.getElementById('results-content');

    // Parse comments
    const comments = commentsText.split('\n').map(c => c.trim()).filter(c => c);

    // Validate - at least one input required
    if (!productName && !sellingPoints && comments.length === 0) {
        errorEl.textContent = '请输入商品名称、卖点或评论至少一项';
        errorEl.style.display = 'block';
        emptyState.style.display = 'none';
        loadingEl.style.display = 'none';
        resultsContent.style.display = 'none';
        return;
    }

    // Show loading state
    btn.disabled = true;
    btn.textContent = '生成中...';
    emptyState.style.display = 'none';
    errorEl.style.display = 'none';
    resultsContent.style.display = 'none';
    loadingEl.style.display = 'block';

    // Reset progress steps
    updateProgressStep(1, '');
    updateProgressStep(2, '');
    updateProgressStep(3, '');

    try {
        const response = await fetch('/api/generate-scripts-sse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_name: productName,
                product_info: productInfo,
                selling_points: sellingPoints,
                comments: comments
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process complete events
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('event: ')) {
                    const eventType = line.slice(7);
                    // Find corresponding data line
                    const dataIndex = lines.indexOf(line) + 1;
                    if (dataIndex < lines.length && lines[dataIndex].startsWith('data: ')) {
                        const data = JSON.parse(lines[dataIndex].slice(6));

                        if (eventType === 'progress') {
                            updateProgressStep(data.step, data.status);
                        } else if (eventType === 'complete') {
                            window.latestResult = data;
                            loadingEl.style.display = 'none';
                            renderResults(data);
                        } else if (eventType === 'error') {
                            throw new Error(data.message || '生成失败');
                        }
                    }
                }
            }
        }

    } catch (error) {
        console.error('Error:', error);
        loadingEl.style.display = 'none';
        errorEl.textContent = '生成失败: ' + error.message;
        errorEl.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = '生成脚本';
    }
}

// Render results with streaming effect
function renderResults(data) {
    const loadingEl = document.getElementById('loading');
    const resultsContent = document.getElementById('results-content');

    loadingEl.style.display = 'none';
    resultsContent.style.display = 'flex';
    resultsContent.innerHTML = '';

    const bestScript = data.best_script;
    const scripts = data.scripts || [];

    // Collect all items to render
    const items = [];

    // Recommended script first
    if (bestScript) {
        items.push({ script: bestScript, isRecommended: true, index: 0 });
    }

    // Other scripts
    scripts.forEach((script, index) => {
        const isBest = bestScript && script.style === bestScript.style;
        if (isBest) return;
        items.push({ script: script, isRecommended: false, index: index + 1 });
    });

    // Render items with streaming effect
    items.forEach((item, i) => {
        setTimeout(() => {
            const html = renderResultItem(item.script, item.isRecommended, item.index);
            resultsContent.insertAdjacentHTML('beforeend', html);

            // Trigger animation
            const lastItem = resultsContent.lastElementChild;
            if (lastItem) {
                // Force reflow
                void lastItem.offsetWidth;
                // Add expanded class for animation
                if (i === 0) {
                    lastItem.classList.add('expanded');
                }
            }

            // Scroll to result
            if (i === items.length - 1) {
                setTimeout(() => {
                    resultsContent.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 200);
            }
        }, i * 200); // 200ms delay between each item
    });
}

// Render single result item
function renderResultItem(script, isRecommended, index) {
    const recommendedClass = isRecommended ? 'recommended' : '';
    const tagText = isRecommended ? '推荐' : script.style;

    return `
        <div class="result-item ${recommendedClass}" onclick="toggleResultCard(this)">
            <div class="result-header">
                <div class="result-title">
                    ${isRecommended ? '<span class="tag">推荐</span>' : ''}
                    <span class="style-name">${script.style}</span>
                    <span class="score">${script.score}分</span>
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="result-content">
                <div class="script-part">
                    <div class="script-part-header">
                        <span class="script-part-label">开头吸引</span>
                        <button class="copy-btn" onclick="event.stopPropagation(); copyText(this, '${escapeHtml(script.opening_hook)}')">复制</button>
                    </div>
                    <div class="script-part-content">${script.opening_hook}</div>
                </div>
                <div class="script-part">
                    <div class="script-part-header">
                        <span class="script-part-label">痛点描述</span>
                        <button class="copy-btn" onclick="event.stopPropagation(); copyText(this, '${escapeHtml(script.pain_point)}')">复制</button>
                    </div>
                    <div class="script-part-content">${script.pain_point}</div>
                </div>
                <div class="script-part">
                    <div class="script-part-header">
                        <span class="script-part-label">解决方案</span>
                        <button class="copy-btn" onclick="event.stopPropagation(); copyText(this, '${escapeHtml(script.solution)}')">复制</button>
                    </div>
                    <div class="script-part-content">${script.solution}</div>
                </div>
                <div class="script-part">
                    <div class="script-part-header">
                        <span class="script-part-label">证明案例</span>
                        <button class="copy-btn" onclick="event.stopPropagation(); copyText(this, '${escapeHtml(script.proof)}')">复制</button>
                    </div>
                    <div class="script-part-content">${script.proof}</div>
                </div>
                <div class="script-part">
                    <div class="script-part-header">
                        <span class="script-part-label">促单话术</span>
                        <button class="copy-btn" onclick="event.stopPropagation(); copyText(this, '${escapeHtml(script.offer)}')">复制</button>
                    </div>
                    <div class="script-part-content">${script.offer}</div>
                </div>
            </div>
            <div class="result-footer">
                <button class="btn-secondary" onclick="event.stopPropagation(); copyFullScript(this, ${index})">复制完整话术</button>
                ${isRecommended ? `
                    <button class="btn-secondary" onclick="event.stopPropagation(); exportScripts('txt')">导出TXT</button>
                    <button class="btn-secondary" onclick="event.stopPropagation(); exportScripts('md')">导出MD</button>
                ` : ''}
            </div>
        </div>
    `;
}
