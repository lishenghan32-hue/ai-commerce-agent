/* ========================================
   极简高级风格 - JavaScript
   ======================================== */

// Toggle advanced inputs
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleAdvanced');
    const advanced = document.querySelector('.advanced-inputs');
    if (toggleBtn && advanced) {
        toggleBtn.addEventListener('click', () => {
            if (advanced.style.display === 'none') {
                advanced.style.display = 'block';
                toggleBtn.innerText = '收起 ▲';
            } else {
                advanced.style.display = 'none';
                toggleBtn.innerText = '展开更多信息 ▼';
            }
        });
    }
});

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

// Rewrite script
async function rewriteScript(btn, index, mode) {
    const script = window.latestResult?.scripts?.[index];
    if (!script) return;

    const originalText = btn.textContent;
    btn.textContent = '改写中...';
    btn.disabled = true;

    // Disable all rewrite buttons in this card
    const card = btn.closest('.result-item');
    const allRewriteBtns = card.querySelectorAll('.rewrite-btn');
    allRewriteBtns.forEach(b => b.disabled = true);

    try {
        const response = await fetch('/api/rewrite-script', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                script: script,
                mode: mode
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || '改写失败');
        }

        const rewritten = await response.json();

        // Update the script in latestResult
        window.latestResult.scripts[index] = {
            ...window.latestResult.scripts[index],
            ...rewritten
        };

        // Update best_script if this is the best
        if (window.latestResult.best_script && window.latestResult.best_script.style === script.style) {
            window.latestResult.best_script = {
                ...window.latestResult.best_script,
                ...rewritten
            };
        }

        // Re-render the result card
        const newHtml = renderResultItem(window.latestResult.scripts[index], window.latestResult.best_script && window.latestResult.best_script.style === script.style, index);
        card.outerHTML = newHtml;

    } catch (err) {
        console.error('改写失败:', err);
        alert('改写失败: ' + err.message);
    } finally {
        // Re-enable buttons
        allRewriteBtns.forEach(b => b.disabled = false);
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

// Parse product URL and auto-fill form
async function parseProductUrl(url) {
    if (!url) return;

    try {
        const response = await fetch('/api/parse-product', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            console.error('Parse failed:', response.status);
            return;
        }

        const data = await response.json();

        // Auto-fill form fields
        if (data.name) {
            document.getElementById('product-name').value = data.name;
        }
        if (data.selling_points) {
            document.getElementById('selling-points').value = data.selling_points;
        }
        if (data.comments && data.comments.length > 0) {
            document.getElementById('comments').value = data.comments.join('\n');
        }

        console.log('Product parsed:', data);
    } catch (error) {
        console.error('Parse error:', error);
    }
}

// Generate scripts with SSE
async function generateScripts() {
    const productUrl = document.getElementById('product-url').value.trim();
    const btn = document.getElementById('generate-btn');

    // Parse product URL and auto-fill form
    if (productUrl) {
        btn.textContent = '🚀 解析商品链接中...';
        btn.disabled = true;
        await parseProductUrl(productUrl);
        btn.disabled = false;
        btn.textContent = '🚀 AI 正在生成中（约3秒）';
    }

    const productName = document.getElementById('product-name').value.trim();
    const productInfo = document.getElementById('product-info').value.trim();
    const sellingPoints = document.getElementById('selling-points').value.trim();
    const commentsText = document.getElementById('comments').value;
    const emptyState = document.getElementById('empty-state');
    const loadingEl = document.getElementById('loading');
    const streamingEl = document.getElementById('streaming');
    const streamingContent = document.getElementById('streamingContent');
    const errorEl = document.getElementById('error');
    const resultsContent = document.getElementById('results-content');

    // Parse comments
    const comments = commentsText.split('\n').map(c => c.trim()).filter(c => c);

    // Validate - at least one input required (including URL)
    if (!productName && !sellingPoints && !productUrl && comments.length === 0) {
        errorEl.textContent = '请输入商品链接、名称、卖点或评论至少一项';
        errorEl.style.display = 'block';
        emptyState.style.display = 'flex';
        loadingEl.style.display = 'none';
        streamingEl.style.display = 'none';
        resultsContent.style.display = 'none';
        return;
    }

    // Show streaming state - hide empty state
    btn.disabled = true;
    btn.textContent = '🚀 AI 正在生成中（约3秒）';
    emptyState.style.display = 'none';
    errorEl.style.display = 'none';
    resultsContent.style.display = 'none';
    loadingEl.style.display = 'none';
    streamingEl.style.display = 'flex';

    // 1. Show skeleton UI immediately
    streamingContent.innerHTML = `
        <div id="thinking-text" class="thinking-text">正在理解用户输入...</div>
        <div class="fake-structure">
            <div class="fake-block" data-field="opening_hook">
                <span class="fake-label">开头吸引：</span><span class="shimmer"></span>
            </div>
            <div class="fake-block" data-field="pain_point">
                <span class="fake-label">痛点描述：</span><span class="shimmer"></span>
            </div>
            <div class="fake-block" data-field="solution">
                <span class="fake-label">解决方案：</span><span class="shimmer"></span>
            </div>
            <div class="fake-block" data-field="proof">
                <span class="fake-label">证明案例：</span><span class="shimmer"></span>
            </div>
            <div class="fake-block" data-field="offer">
                <span class="fake-label">促单话术：</span><span class="shimmer"></span>
            </div>
        </div>
    `;

    // 2. Start thinking text cycling
    const thinkingSteps = [
        "正在理解用户输入...",
        "正在分析评论情绪...",
        "正在提炼核心卖点...",
        "正在构建话术结构...",
        "正在优化表达..."
    ];
    let thinkingIndex = 0;
    let thinkingEl = document.getElementById('thinking-text');
    let thinkingTimer = setInterval(() => {
        if (thinkingEl) {
            thinkingEl.textContent = thinkingSteps[thinkingIndex % thinkingSteps.length];
            thinkingIndex++;
        }
    }, 1200);

    // Reset progress steps
    updateProgressStep(1, '');
    updateProgressStep(2, '');
    updateProgressStep(3, '');

    // Streaming state variables
    let currentField = null;
    let currentSection = null;
    let accumulatedContent = {};
    let isCompleted = false;

    // 3. Use EventSource for true SSE
    const params = new URLSearchParams({
        product_url: productUrl,
        product_name: productName,
        product_info: productInfo,
        selling_points: sellingPoints,
        comments: JSON.stringify(comments)
    });

    const eventSource = new EventSource(`/api/generate-scripts-sse?${params.toString()}`);

    // Log when connection opens
    eventSource.onopen = function() {
        console.log('EventSource connected');
    };

    eventSource.onerror = function(error) {
        console.error('EventSource error:', error);
    };

    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);

            if (data.step !== undefined) {
                updateProgressStep(data.step, data.status);
            }
        } catch (e) {
            console.error('Parse error:', e);
        }
    };

    eventSource.addEventListener('progress', function(event) {
        try {
            const data = JSON.parse(event.data);
            updateProgressStep(data.step, data.status);
        } catch (e) {
            console.error('Progress parse error:', e);
        }
    });

    eventSource.addEventListener('section', function(event) {
        try {
            const data = JSON.parse(event.data);

            // Hide thinking text when first section arrives
            if (thinkingEl) thinkingEl.style.display = 'none';
            clearInterval(thinkingTimer);

            // Replace skeleton block with real section
            currentField = data.field;
            accumulatedContent[currentField] = '';
            currentSection = createStreamingSection(data.label, data.field);

            // Find and replace skeleton block
            const skeletonBlock = document.querySelector(`.fake-block[data-field="${currentField}"]`);
            if (skeletonBlock) {
                skeletonBlock.replaceWith(currentSection.element);
            } else {
                streamingContent.appendChild(currentSection.element);
            }
            currentSection.element.classList.add('fade-in');
            streamingEl.scrollTop = streamingEl.scrollHeight;
        } catch (e) {
            console.error('Section parse error:', e);
        }
    });

    eventSource.addEventListener('chunk', function(event) {
        try {
            const data = JSON.parse(event.data);

            // Accumulate content and type it
            if (currentField && currentSection) {
                accumulatedContent[currentField] += data.content;
                // Use typewriter effect
                typeWriter(currentSection.textEl, accumulatedContent[currentField], currentSection.cursor);
                streamingEl.scrollTop = streamingEl.scrollHeight;
            }
        } catch (e) {
            console.error('Chunk parse error:', e);
        }
    });

    eventSource.addEventListener('complete', function(event) {
        try {
            const data = JSON.parse(event.data);
            isCompleted = true;
            clearInterval(thinkingTimer);
            eventSource.close();

            // Fade out skeleton and show results
            const fakeStructure = document.querySelector('.fake-structure');
            if (fakeStructure) {
                fakeStructure.style.transition = 'opacity 0.3s';
                fakeStructure.style.opacity = '0';
                setTimeout(() => {
                    streamingEl.style.display = 'none';
                    renderResults(data);
                }, 300);
            } else {
                streamingEl.style.display = 'none';
                renderResults(data);
            }

            btn.disabled = false;
            btn.textContent = '生成脚本';
        } catch (e) {
            console.error('Complete parse error:', e);
        }
    });

    eventSource.addEventListener('error', function(event) {
        // Don't treat as error if already completed
        if (isCompleted) {
            console.log('Stream completed, ignoring error');
            return;
        }

        console.error('SSE Error:', event);
        console.error('Ready state:', eventSource.readyState);

        // Check if it's a genuine error or just connection end
        if (eventSource.readyState === EventSource.CLOSED) {
            console.log('Connection closed normally');
            return;
        }

        clearInterval(thinkingTimer);
        eventSource.close();
        streamingEl.style.display = 'none';
        errorEl.textContent = '生成失败: SSE连接错误';
        errorEl.style.display = 'block';
        btn.disabled = false;
        btn.textContent = '生成脚本';
    });
}

// Create streaming section element
function createStreamingSection(label, field) {
    const element = document.createElement('div');
    element.className = 'streaming-section';

    const labelEl = document.createElement('div');
    labelEl.className = 'streaming-section-label';
    labelEl.textContent = label;

    const textEl = document.createElement('div');
    textEl.className = 'streaming-text';

    const cursor = document.createElement('span');
    cursor.className = 'streaming-cursor';

    textEl.appendChild(cursor);
    element.appendChild(labelEl);
    element.appendChild(textEl);

    return {
        element: element,
        textEl: textEl,
        cursor: cursor,
        field: field
    };
}

// Typewriter effect function
function typeWriter(textEl, fullText, cursor) {
    // Remove cursor temporarily
    if (cursor && cursor.parentNode) {
        cursor.parentNode.removeChild(cursor);
    }

    let currentText = textEl.textContent;
    let targetText = fullText;

    if (currentText === targetText) return;

    // Calculate new characters to add
    let newChars = targetText.slice(currentText.length);

    // Add characters one by one with small delay
    let i = 0;
    function type() {
        if (i < newChars.length) {
            textEl.textContent = currentText + newChars.slice(0, i + 1);
            i++;
            setTimeout(type, 15);
        } else {
            // Add cursor back at the end
            textEl.appendChild(cursor);
        }
    }
    type();
}

// Append chunk with typewriter effect (legacy)
function appendChunk(section, chunk) {
    // Remove cursor temporarily
    if (section.cursor.parentNode) {
        section.cursor.parentNode.removeChild(section.cursor);
    }

    // Add new content
    section.textEl.textContent += chunk;

    // Add cursor back
    section.textEl.appendChild(section.cursor);
}

// Render results with streaming effect
function renderResults(data) {
    const loadingEl = document.getElementById('loading');
    const streamingEl = document.getElementById('streaming');
    const resultsContent = document.getElementById('results-content');

    loadingEl.style.display = 'none';
    streamingEl.style.display = 'none';
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

    return `
        <div class="result-item ${recommendedClass}" onclick="toggleResultCard(this)">
            <div class="script-header">
                <div class="script-meta">
                    ${isRecommended ? '<span class="tag">推荐</span>' : ''}
                    <span class="style-name">${script.style}</span>
                    <span class="score">${script.score}分</span>
                </div>
                <div class="quick-actions">
                    <button onclick="event.stopPropagation(); rewriteScript(this, ${index}, '强化转化')">🔥 强化</button>
                    <button onclick="event.stopPropagation(); rewriteScript(this, ${index}, '更口语')">😂 口语</button>
                    <button onclick="event.stopPropagation(); rewriteScript(this, ${index}, '更理性')">🧠 理性</button>
                    <button onclick="event.stopPropagation(); rewriteScript(this, ${index}, '更简短')">✂️ 精简</button>
                </div>
            </div>
            <div class="result-header">
                <div class="result-title">
                    <span class="toggle-icon">▼</span>
                </div>
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
