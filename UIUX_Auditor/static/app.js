// AI UI/UX Auditor - Hackathon Excellence v2.2
const messages = [
    "Analyzing website architecture...",
    "Scanning HTML for SEO elements...",
    "Measuring page load performance...",
    "Checking mobile viewport responsiveness...",
    "Waiting for AI to generate UI insights...",
    "Almost done, compiling report..."
];

let msgInterval;
let lastIssues = [];
let lastAuditData = null; // Added for chatbot context

async function startAudit() {
    const urlInput = document.getElementById('urlInput').value;
    const errorMsg = document.getElementById('errorMsg');

    if (!urlInput) {
        showError("Please enter a valid website URL.");
        return;
    }
    errorMsg.innerText = "";

    // Hide input, show loading
    document.getElementById('inputSection').classList.add('hide');
    document.getElementById('dashboardSection').classList.add('hide');
    document.getElementById('loadingSection').classList.remove('hide');

    // Cycle messages
    let msgIndex = 0;
    const loadingText = document.getElementById('loadingText');
    loadingText.innerText = messages[0];
    msgInterval = setInterval(() => {
        msgIndex = (msgIndex + 1) % messages.length;
        loadingText.innerText = messages[msgIndex];
    }, 3000);

    // Fetch call
    try {
        const response = await fetch('/api/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlInput })
        });

        const data = await response.json();
        lastAuditData = data; // CAPTURE FOR CHATBOT

        clearInterval(msgInterval);
        if (data.error) {
            showError(data.error);
        } else {
            populateDashboard(data);
            // Show chatbot after success
            const chatBtn = document.getElementById('chatToggleBtn');
            if (chatBtn) chatBtn.classList.remove('hide');
        }
    } catch (err) {
        clearInterval(msgInterval);
        showError("An error occurred while communicating with the server.");
        console.error(err);
    }
}

function showError(msg) {
    document.getElementById('loadingSection').classList.add('hide');
    document.getElementById('inputSection').classList.remove('hide');
    document.getElementById('errorMsg').innerText = msg;
}

function populateDashboard(data) {
    lastAuditData = data; // CRITICAL: Save for chatbot context and variant switching
    document.getElementById('loadingSection').classList.add('hide');
    document.getElementById('dashboardSection').classList.remove('hide');

    document.getElementById('reportUrl').innerText = data.url;

    // Grade and Health
    document.getElementById('gradeVal').innerText = data.scores["Grade"] || "N/A";
    document.getElementById('healthVal').innerText = data.scores["Health"] || "N/A";
    
    // Animate Final Score Bar
    animateLinearScore('finalScoreBar', 'finalScoreVal', data.scores["Final Score"]);

    // Animate Circular Scores
    animateCircularScore('uiuxCircle', 'uiuxScore', data.scores["UI/UX Score"]);
    animateCircularScore('perfCircle', 'perfScore', data.scores["Performance Score"]);
    animateCircularScore('accessCircle', 'accessScore', data.scores["Accessibility Score"]);
    animateCircularScore('seoCircle', 'seoScore', data.scores["SEO Score"]);
    animateCircularScore('bpCircle', 'bpScore', data.scores["Best Practices Score"]);

    // Executive Summary
    const execSummaryCard = document.getElementById('execSummaryCard');
    const execSummaryText = document.getElementById('execSummaryText');
    if (data.executive_summary) {
        execSummaryText.innerText = data.executive_summary;
        execSummaryCard.style.display = 'block';
    } else {
        execSummaryCard.style.display = 'none';
    }

    // Populate UI/UX Breakdown
    const uiuxBreakdownList = document.getElementById('uiuxBreakdownList');
    uiuxBreakdownList.innerHTML = '';
    if (data.ui_ux_breakdown) {
        for (const [key, val] of Object.entries(data.ui_ux_breakdown)) {
            const wrap = document.createElement('div');
            wrap.style.marginBottom = "8px";
            wrap.innerHTML = `
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 4px; color: var(--text-secondary);">
                    <span>${key}</span><span>${val}/100</span>
                </div>
                <div style="width: 100%; height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden;">
                    <div style="width: ${val}%; height: 100%; background: var(--accent-primary); border-radius: 3px;"></div>
                </div>
            `;
            uiuxBreakdownList.appendChild(wrap);
        }
    }

    // Populate Business Impact
    const businessImpactList = document.getElementById('businessImpactList');
    businessImpactList.innerHTML = '';
    if (data.business_impact) {
        const icons = {
            "digital_visibility": "fa-globe",
            "user_engagement": "fa-users",
            "conversion_rate": "fa-chart-line",
            "trust": "fa-shield-halved",
            "lead_generation": "fa-bullseye"
        };
        for (const [key, val] of Object.entries(data.business_impact)) {
            if (val && val !== "N/A") {
                const title = key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                const icon = icons[key] || "fa-check";
                
                const li = document.createElement('li');
                li.style.display = "flex";
                li.style.gap = "12px";
                li.style.alignItems = "flex-start";
                li.innerHTML = `
                    <div style="background: rgba(139, 92, 246, 0.1); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--accent-secondary); flex-shrink: 0; margin-top: 2px;">
                        <i class="fa-solid ${icon}"></i>
                    </div>
                    <div>
                        <strong style="display: block; font-size: 0.95rem; color: var(--text-primary);">${title}</strong>
                        <span style="font-size: 0.9rem; color: var(--text-secondary);">${val}</span>
                    </div>
                `;
                businessImpactList.appendChild(li);
            }
        }
    }

    // Populate Key Issues
    const issuesList = document.getElementById('issuesList');
    issuesList.innerHTML = '';
    if (!data.key_issues || data.key_issues.length === 0) {
        issuesList.innerHTML = "<div style='color: var(--text-secondary);'>No major issues found!</div>";
    } else {
        data.key_issues.forEach(i => {
            const severityColor = i.severity === "High" ? "var(--error)" : (i.severity === "Medium" ? "var(--warning)" : "var(--accent-primary)");
            const div = document.createElement('div');
            div.style.padding = "10px 15px";
            div.style.background = "rgba(15, 23, 42, 0.02)";
            div.style.borderLeft = `3px solid ${severityColor}`;
            div.style.borderRadius = "0 8px 8px 0";
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <strong style="color: var(--text-primary);">${i.title}</strong>
                    <span style="font-size: 0.75rem; font-weight: 700; background: ${severityColor}; color: white; padding: 2px 8px; border-radius: 12px;">${i.severity} Priority</span>
                </div>
                <p style="margin: 0; font-size: 0.9rem; color: var(--text-secondary);">${i.description}</p>
            `;
            issuesList.appendChild(div);
        });
    }

    // Populate Recommendations
    const recList = document.getElementById('recommendationsList');
    recList.innerHTML = '';
    if (!data.recommendations || data.recommendations.length === 0) {
        recList.innerHTML = "<div style='color: var(--text-secondary);'>No recommendations available.</div>";
    } else {
        data.recommendations.forEach(r => {
            const priorityColor = r.priority === "High" ? "var(--success)" : (r.priority === "Medium" ? "var(--accent-primary)" : "var(--text-secondary)");
            const div = document.createElement('div');
            div.style.padding = "10px 15px";
            div.style.background = "rgba(16, 185, 129, 0.05)";
            div.style.border = "1px solid rgba(16, 185, 129, 0.2)";
            div.style.borderRadius = "8px";
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <strong style="color: var(--text-primary);"><i class="fa-solid fa-arrow-right" style="color: var(--success); margin-right: 5px;"></i> ${r.title}</strong>
                    <span style="font-size: 0.75rem; font-weight: 700; background: ${priorityColor}; color: white; padding: 2px 8px; border-radius: 12px;">${r.priority} Value</span>
                </div>
                <p style="margin: 0; font-size: 0.9rem; color: var(--text-secondary);">${r.description}</p>
            `;
            recList.appendChild(div);
        });
    }

    // Render Heatmap (using titles of key issues as proxy)
    lastIssues = data.key_issues ? data.key_issues.map(i => i.title) : [];
    renderHeatmap('heatmapCanvas', lastIssues);

    // Set Up Iframes & Screenshot
    const origIframe = document.getElementById('originalIframe');
    const origScreenshot = document.getElementById('originalScreenshot');
    const fallbackMsg = document.getElementById('iframeFallbackMsg');
    
    let urlToLoad = data.url;
    if (!urlToLoad.startsWith('http://') && !urlToLoad.startsWith('https://')) {
        urlToLoad = 'https://' + urlToLoad;
    }
    
    // RESTORE INTERACTION: Use the Proxy in an Iframe as the PRIMARY view
    const loadProxy = () => {
        console.log("Loading interactive proxy for:", urlToLoad);
        origIframe.src = `/proxy?url=${encodeURIComponent(urlToLoad)}`;
        origIframe.style.display = 'block';
        if (origScreenshot) origScreenshot.style.display = 'none';
        
        if (fallbackMsg) {
            fallbackMsg.innerHTML = '<i class="fa-solid fa-bolt"></i> Interactive Preview (via Proxy)';
            fallbackMsg.style.display = 'block';
        }
    };

    // We still have the screenshot for high-fidelity backup
    if (data.screenshot) {
        origScreenshot.src = `data:image/jpeg;base64,${data.screenshot}`;
    }
    
    // Default to interactive mode
    loadProxy();

    // AI Redesign Rendering
    const aiIframe = document.getElementById('aiIframe');
    const aiCode = data.generated_code || "<h2>No code generated</h2>";
    document.getElementById('generatedCodeBlock').textContent = aiCode;
    
    // Reset variant selector
    const variantSelect = document.getElementById('redesignVariantSelect');
    if (variantSelect) variantSelect.value = "-1";
    const variantInfo = document.getElementById('variantInfo');
    if (variantInfo) variantInfo.style.display = 'none';

    // Write AI code to iframe blob/data uri
    const blob = new Blob([aiCode], { type: 'text/html' });
    const redesignUrl = URL.createObjectURL(blob);
    aiIframe.src = redesignUrl;

    // Prepare Slider
    const sliderOriginalImg = document.getElementById('sliderOriginalImg');
    const sliderAiIframe = document.getElementById('sliderAiIframe');
    if (data.screenshot) {
        sliderOriginalImg.src = `data:image/jpeg;base64,${data.screenshot}`;
    }
    sliderAiIframe.src = redesignUrl;
    initSlider();
}

function changeRedesignVariant(index) {
    if (!lastAuditData) return;
    
    let html = "";
    let layout = "Default";
    let style = "Default";
    
    if (index === "-1") {
        html = lastAuditData.generated_code;
        document.getElementById('variantInfo').style.display = 'none';
    } else {
        const variant = lastAuditData.bonus_redesigns[index];
        if (!variant) return;
        html = variant.html;
        layout = variant.layout;
        style = variant.style;
        
        document.getElementById('variantLayout').innerText = layout;
        document.getElementById('variantStyle').innerText = style;
        document.getElementById('variantInfo').style.display = 'block';
    }
    
    const aiIframe = document.getElementById('aiIframe');
    document.getElementById('generatedCodeBlock').textContent = html;
    const blob = new Blob([html], { type: 'text/html' });
    aiIframe.src = URL.createObjectURL(blob);
}

function renderHeatmap(canvasId, issues) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width = canvas.offsetWidth;
    const h = canvas.height = canvas.offsetHeight;

    ctx.clearRect(0, 0, w, h);

    // Simulated hot zones based on common layouts
    const zones = [
        { x: w * 0.15, y: h * 0.1, r: 60, intensity: 0.8 }, // Logo
        { x: w * 0.5, y: h * 0.3, r: 120, intensity: 1.0 }, // Hero Text
        { x: w * 0.5, y: h * 0.5, r: 80, intensity: 0.9 },  // CTA Area
        { x: w * 0.8, y: h * 0.1, r: 50, intensity: 0.6 }  // Nav Links
    ];

    // Add some random "interest zones" if issues are found
    issues.forEach(() => {
        zones.push({
            x: Math.random() * w,
            y: Math.random() * h,
            r: 40 + Math.random() * 60,
            intensity: 0.4 + Math.random() * 0.4
        });
    });

    zones.forEach(z => {
        const grd = ctx.createRadialGradient(z.x, z.y, 0, z.x, z.y, z.r);
        grd.addColorStop(0, `rgba(255, 0, 0, ${z.intensity})`);
        grd.addColorStop(0.5, `rgba(255, 255, 0, ${z.intensity * 0.5})`);
        grd.addColorStop(1, 'rgba(0, 255, 0, 0)');

        ctx.fillStyle = grd;
        ctx.beginPath();
        ctx.arc(z.x, z.y, z.r, 0, Math.PI * 2);
        ctx.fill();
    });
}

function setPersona() {
    const personas = [
        { name: "The Minimalist", quote: "Simplicity is the ultimate sophistication. Eliminate the noise.", icon: "fa-leaf" },
        { name: "UX Critic", quote: "I've seen better. Let's fix this mess.", icon: "fa-user-tie" },
        { name: "Conversion Pro", quote: "Where is the button? If they can't see it, they won't click it.", icon: "fa-chart-line" }
    ];
    const p = personas[Math.floor(Math.random() * personas.length)];
    document.getElementById('personaName').innerText = p.name;
    document.getElementById('personaQuote').innerText = `"${p.quote}"`;
    document.querySelector('.persona-avatar i').className = `fa-solid ${p.icon}`;
}

function animateCircularScore(circleId, textId, targetScore) {
    const circle = document.getElementById(circleId);
    const textObj = document.getElementById(textId);
    if (!circle || !textObj) return;
    
    let currentScore = 0;
    const duration = 1500;
    const interval = 20;
    const step = targetScore / (duration / interval);
    
    // Determine color based on hackathon tier
    let color = '#ef4444'; // Red for poor
    if (targetScore >= 90) color = '#10b981'; // Green for excellent
    else if (targetScore >= 70) color = '#f59e0b'; // Amber for good
    else if (targetScore >= 50) color = '#3b82f6'; // Blue for average
    
    // Set text color explicitly
    textObj.style.color = color;
    
    const timer = setInterval(() => {
        currentScore += step;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(timer);
        }
        textObj.innerText = Math.round(currentScore);
        
        // Update conic gradient
        circle.style.background = `conic-gradient(${color} ${currentScore}%, rgba(0,0,0,0.05) ${currentScore}%)`;
    }, interval);
}

function animateLinearScore(barId, textId, target) {
    let current = 0;
    const bar = document.getElementById(barId);
    const textEl = document.getElementById(textId);

    // Choose color based on score
    let color = "#ef4444"; // red
    if (target >= 50) color = "#f59e0b"; // yellow
    if (target >= 80) color = "#10b981"; // green

    const interval = setInterval(() => {
        if (current >= target) {
            clearInterval(interval);
            current = target;
            if(bar) {
                bar.style.width = target + '%';
                bar.style.background = color;
            }
        }
        if(textEl) textEl.innerText = current;
        current += 1; 
    }, 15);
    
    if (target === 0) {
        if(textEl) textEl.innerText = 0;
        if(bar) bar.style.width = '0%';
    }
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view-pane').forEach(v => v.classList.add('hide'));

    const btns = document.querySelectorAll('.tab-btn');
    if (tab === 'preview') {
        btns[0].classList.add('active');
        document.getElementById('previewTab').classList.remove('hide');
    } else if (tab === 'slider') {
        btns[1].classList.add('active');
        document.getElementById('sliderTab').classList.remove('hide');
        // Re-init slider center if needed
        const slider = document.getElementById('sliderAfterLayer');
        const handle = document.getElementById('sliderHandle');
        if(slider && handle) {
            slider.style.width = '50%';
            handle.style.left = '50%';
        }
    } else {
        btns[2].classList.add('active');
        document.getElementById('codeTab').classList.remove('hide');
    }
}

function copyCode() {
    const codeBlock = document.getElementById('generatedCodeBlock');
    const code = codeBlock ? codeBlock.innerText : '';

    // Fallback method works on http:// (local dev) where navigator.clipboard is blocked
    const ta = document.createElement('textarea');
    ta.value = code;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    ta.style.top = '-9999px';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
        const success = document.execCommand('copy');
        const copyBtn = document.getElementById('mainCopyBtn');
        if (copyBtn) {
            const orig = copyBtn.innerHTML;
            copyBtn.innerHTML = success
                ? '<i class="fa-solid fa-check"></i> Copied!'
                : '<i class="fa-solid fa-xmark"></i> Failed';
            setTimeout(() => { copyBtn.innerHTML = orig; }, 2000);
        }
    } catch (e) {
        alert('Could not copy. Please select the code and press Ctrl+C manually.');
    }
    document.body.removeChild(ta);
}

function resetApp() {
    document.getElementById('dashboardSection').classList.add('hide');
    document.getElementById('inputSection').classList.remove('hide');
    document.getElementById('urlInput').value = '';
}

function downloadPDF() {
    // Rely on the newly added @media print CSS rules for formatting.
    // This is 100% reliable compared to client-side canvas capture logic.
    window.print();
}

function toggleFullscreen(containerId) {
    const container = document.getElementById(containerId);
    container.classList.toggle('fullscreen');

    // Toggle icon
    const btn = container.querySelector('.expand-btn i');
    if (container.classList.contains('fullscreen')) {
        btn.className = 'fa-solid fa-compress';
    } else {
        btn.className = 'fa-solid fa-expand';
    }

    // Attempt to re-render heatmap to adjust to new size
    try {
        renderHeatmap('heatmapCanvas', lastIssues);
    } catch (e) { }
}

// --- AI Chatbot Logic ---

function toggleChat() {
    const widget = document.getElementById('aiChatWidget');
    const overlay = document.getElementById('chatOverlay');
    if (!widget || !overlay) return;

    widget.classList.toggle('hide');
    overlay.classList.toggle('hide');

    if (!widget.classList.contains('hide')) {
        document.getElementById('chatInput').focus();
        document.body.style.overflow = 'hidden'; // Lock scrolling
    } else {
        document.body.style.overflow = ''; // Restore scrolling
    }
}

function handleChatKey(e) {
    if (e.key === 'Enter') sendChatMessage();
}

function sendQuickMsg(text) {
    appendMessage('user', text);
    processChatResponse(text);
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    appendMessage('user', text);

    // Add loading state
    const loadingId = 'bot-loading-' + Date.now();
    appendMessage('bot', '<div class="typing-indicator"><span></span><span></span><span></span></div>', loadingId);

    await processChatResponse(text, loadingId);
}

function appendMessage(side, text, id = null) {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    const wrapper = document.createElement('div');
    wrapper.className = `message ${side}`;
    if (id) wrapper.id = id;

    if (side === 'bot') {
        wrapper.innerHTML = `
            <div class="message-avatar bot">
                <img src="static/robot_avatar.png" alt="AI">
            </div>
            <div class="message-content">${text}</div>
        `;
    } else {
        wrapper.innerHTML = `
            <div class="message-avatar user">
                <i class="fa-solid fa-user"></i>
            </div>
            <div class="message-content">${text}</div>
        `;
    }

    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
}

async function processChatResponse(userMsg, loadingId = null) {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMsg,
                audit_context: lastAuditData
            })
        });

        const data = await response.json();

        if (loadingId) {
            const loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();
        }

        if (data.reply) {
            appendMessage('bot', formatChatMsg(data.reply));
        } else {
            appendMessage('bot', "I'm focusing on your audit results. Ask me anything about UI/UX, SEO, or performance!");
        }
    } catch (err) {
        console.error("Chat Error:", err);
        if (loadingId) document.getElementById(loadingId)?.remove();
        appendMessage('bot', "Connection lost. Please ensure the server is running.");
    }
}

function formatChatMsg(text) {
    // Basic Markdown to HTML
    let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Code blocks with copy button
    html = html.replace(/```([\s\S]*?)```/g, function (match, code) {
        let parts = code.split('\n');
        let lang = '';
        if (parts[0].trim().match(/^[a-z]+$/i)) {
            lang = parts.shift().trim();
        }
        let cleanCode = parts.join('\n').trim();
        let escapedCode = cleanCode.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

        return `<div class="code-block-wrapper">
                    <div class="code-header">
                        <span class="language">${lang}</span>
                        <button class="copy-btn" onclick="copyCode(this)"><i class="fa-regular fa-copy"></i> Copy code</button>
                    </div>
                    <pre><code class="language-${lang}">${escapedCode}</code></pre>
                </div>`;
    });

    // Safe newline to BR conversion (avoiding inside <pre>)
    let chunks = html.split(/(<div class="code-block-wrapper">[\s\S]*?<\/div>)/);
    for (let i = 0; i < chunks.length; i++) {
        if (!chunks[i].startsWith('<div class="code-block-wrapper">')) {
            chunks[i] = chunks[i].replace(/\n/g, '<br>');
        }
    }
    return chunks.join('');
}

// Global scope copy function for inline onclick handler
window.copyCode = function (button) {
    const pre = button.parentElement.nextElementSibling;
    const code = pre ? pre.textContent : '';

    const originalText = button.innerHTML;

    // Modern clipboard API (requires HTTPS) with fallback for local dev (http)
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(code).then(() => {
            button.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => { button.innerHTML = originalText; }, 2000);
        }).catch(() => fallbackCopy(code, button, originalText));
    } else {
        fallbackCopy(code, button, originalText);
    }
};

function fallbackCopy(text, button, originalText) {
    // Create a temporary textarea, select and copy
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    ta.style.top = '-9999px';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
        document.execCommand('copy');
        button.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
    } catch (e) {
        button.innerHTML = '<i class="fa-solid fa-xmark"></i> Failed';
    }
    document.body.removeChild(ta);
    setTimeout(() => { button.innerHTML = originalText; }, 2000);
}


/**
 * Switch Preview container sizes (S, M, L)
 * @param {string} size - 'sm', 'md', or 'lg'
 */
function setPreviewSize(size) {
    const section = document.querySelector('.comparison-section');
    if (!section) return;
    
    // Remove all height classes
    section.classList.remove('h-sm', 'h-md', 'h-lg');
    // Add new height class
    section.classList.add(`h-${size}`);
    
    // Update active state of buttons
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.classList.remove('active');
        // Match by text or by the size passed in
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(`'${size}'`)) {
            btn.classList.add('active');
        }
    });

    // Trigger resize for any canvas elements (like heatmap)
    // to ensure they adjust to the new container size
    window.dispatchEvent(new Event('resize'));
}

function renderBadges(scores) {
    const container = document.getElementById('badgeContainer');
    if (!container) return;
    container.innerHTML = '';

    const final = scores["Final Score"] || 0;
    const uiux = scores["UI/UX Score"] || 0;
    const perf = scores["Performance Score"] || 0;

    // AI Pioneer (Always)
    container.innerHTML += `<div class="achievement-badge badge-pioneer" title="Early adopter of AI-driven design auditing."><i class="fa-solid fa-microchip"></i> AI Pioneer</div>`;

    // Merit Badges (Lowered drastically for demo purposes)
    if (final >= 50) {
        container.innerHTML += `<div class="achievement-badge badge-king" title="Top-tier performance and design excellence."><i class="fa-solid fa-crown"></i> Conversion King</div>`;
    } else if (final > 0) {
        container.innerHTML += `<div class="achievement-badge badge-specialist" title="Audit completed with actionable growth points."><i class="fa-solid fa-chart-line"></i> Growth Ready</div>`;
    }

    if (uiux >= 40) {
        container.innerHTML += `<div class="achievement-badge badge-visionary" title="Exceptional visual hierarchy and modern aesthetics."><i class="fa-solid fa-unicorn"></i> UX Visionary</div>`;
    }

    if (perf >= 40) {
        container.innerHTML += `<div class="achievement-badge badge-specialist" title="Optimized codebase and fast delivery."><i class="fa-solid fa-bolt"></i> Speed Demon</div>`;
    }
}

function initSlider() {
    const container = document.getElementById('sliderContainer');
    const after = document.getElementById('sliderAfterLayer');
    const handle = document.getElementById('sliderHandle');
    if (!container || !after || !handle) return;

    let isDragging = false;

    const moveSlider = (e) => {
        if (!isDragging) return;
        const rect = container.getBoundingClientRect();
        let x = (e.pageX || e.touches[0].pageX) - rect.left;
        
        // Bounds
        if (x < 0) x = 0;
        if (x > rect.width) x = rect.width;

        const percent = (x / rect.width) * 100;
        after.style.width = percent + '%';
        handle.style.left = percent + '%';
    };

    handle.addEventListener('mousedown', () => isDragging = true);
    window.addEventListener('mouseup', () => isDragging = false);
    window.addEventListener('mousemove', moveSlider);

    handle.addEventListener('touchstart', () => isDragging = true);
    window.addEventListener('touchend', () => isDragging = false);
    window.addEventListener('touchmove', moveSlider);
}

// Ensure Medium is the default visual state on load
document.addEventListener('DOMContentLoaded', () => {
    // We already have h-md active via the HTML class if we added it, 
    // but this ensures the JS state matches if needed.
});
