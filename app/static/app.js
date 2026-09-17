// In-memory Session UUID state (persists across turns during page life)
let currentSessionId = null;
let currentMode = 'chat';

// Helper to escape HTML characters safely
function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Switch between Chat and JSON mode
function switchMode(mode) {
    currentMode = mode;
    const tabChat = document.getElementById('tabChat');
    const tabJson = document.getElementById('tabJson');
    const chatSection = document.getElementById('chatSection');
    const formSection = document.getElementById('formSection');

    if (mode === 'chat') {
        tabChat.classList.add('active');
        tabJson.classList.remove('active');
        chatSection.classList.remove('hidden');
        formSection.classList.add('hidden');
    } else {
        tabJson.classList.add('active');
        tabChat.classList.remove('active');
        formSection.classList.remove('hidden');
        chatSection.classList.add('hidden');
    }
}

// Show/Hide Loading Overlay
function setLoading(loading) {
    const overlay = document.getElementById('loadingOverlay');
    if (loading) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

// Format reasoning summary into structured paragraphs, headers, and callouts
function formatReasoningHTML(text) {
    if (!text) return '';

    // Short response (e.g., simple clarifying question)
    if (text.length < 180 && !text.includes('**')) {
        return `<div class="clarifying-box">${escapeHTML(text)}</div>`;
    }

    let escaped = escapeHTML(text);

    // Replace Markdown bold formatting **text** with clean <strong> callouts
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Split text into paragraphs by double line breaks or single line breaks
    const rawParagraphs = escaped.split(/\n\s*\n|\n/);
    const validParagraphs = rawParagraphs.map(p => p.trim()).filter(p => p.length > 0);

    let paragraphsHTML = '';
    validParagraphs.forEach(para => {
        if (para.startsWith('<strong>')) {
            paragraphsHTML += `<div class="reasoning-para section-para">${para}</div>`;
        } else {
            paragraphsHTML += `<div class="reasoning-para">${para}</div>`;
        }
    });

    return `
        <div class="reasoning-card">
            <div class="reasoning-card-header">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                <span>MULTI-METRIC ECOLOGICAL CAUSAL ANALYSIS</span>
            </div>
            <div class="reasoning-body">
                ${paragraphsHTML}
            </div>
        </div>
    `;
}

// Format recommendations as distinct scannable cards with clean SVG icons
function renderRecommendationsHTML(recs) {
    if (!recs || recs.length === 0) return '';

    let html = '<div style="margin-top: 1.25rem; font-weight:700; font-size:13px; color:var(--primary); font-family:var(--font-mono); letter-spacing:0.8px;">EVIDENCE-BACKED RESTORATION INTERVENTIONS:</div>';

    recs.forEach((rec, idx) => {
        const metricsBadges = (rec.impacted_metrics || []).map(m => `<span class="badge badge-metric">${escapeHTML(m)}</span>`).join(' ');

        html += `
            <div class="recommendation-card">
                <div class="rec-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
                        <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                    </svg>
                    <span>Intervention ${idx + 1}:</span> ${escapeHTML(rec.intervention)}
                </div>
                <div class="rec-mechanism">
                    <strong>Scientific Mechanism:</strong> ${escapeHTML(rec.mechanism)}
                </div>
                <div class="rec-badges">
                    ${metricsBadges}
                    <span class="badge badge-improvement">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                        ${escapeHTML(rec.expected_improvement || 'Quantified Restoration')}
                    </span>
                    <span class="badge badge-horizon">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        ${escapeHTML(rec.time_horizon || 'medium')} term
                    </span>
                </div>
                <div class="rec-citation">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                    <span>Source Citation:</span> ${escapeHTML(rec.citation)} (Confidence: ${escapeHTML(rec.confidence || 'high')})
                </div>
            </div>
        `;
    });

    return html;
}

// Append bubble to chat feed
function appendChatBubble(role, text, recommendations = null) {
    const feed = document.getElementById('chatFeed');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    const isAssistant = role === 'assistant';
    
    const avatarSVG = isAssistant ? `
        <div class="avatar assistant-avatar">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
        </div>` : `
        <div class="avatar user-avatar">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
            </svg>
        </div>`;
        
    const sender = isAssistant ? 'AI Environmental Scientist' : 'User Request';

    let bodyHTML = isAssistant ? formatReasoningHTML(text) : escapeHTML(text);

    if (recommendations && recommendations.length > 0) {
        bodyHTML += renderRecommendationsHTML(recommendations);
    }

    bubble.innerHTML = `
        <div class="bubble-header">
            ${avatarSVG}
            <span class="bubble-sender">${sender}</span>
        </div>
        <div class="bubble-body">${bodyHTML}</div>
    `;

    feed.appendChild(bubble);
    feed.scrollTop = feed.scrollHeight;
}

// Update Active Metrics State Panel
function updateMetricsPanel(metrics) {
    const container = document.getElementById('metricsTags');
    if (!metrics || Object.keys(metrics).length === 0) {
        container.innerHTML = '<span class="empty-state">No metrics extracted yet.</span>';
        return;
    }

    let html = '';
    for (const [key, val] of Object.entries(metrics)) {
        if (val) {
            html += `<div class="metric-tag"><span>${escapeHTML(key)}</span><strong>${escapeHTML(String(val))}</strong></div>`;
        }
    }
    container.innerHTML = html;
}

// Update Retrieval Trace Panel
function updateTracePanel(trace) {
    const container = document.getElementById('traceFeed');
    if (!trace || trace.length === 0) {
        container.innerHTML = '<span class="empty-state">Retrieved vector chunks will appear here after query execution.</span>';
        return;
    }

    let html = '';
    trace.forEach(item => {
        html += `
            <div class="trace-item">
                <div class="trace-item-title">${escapeHTML(item.source_title || 'Reference Chunk')}</div>
                <div class="trace-item-meta">Category: ${escapeHTML(item.category || 'general')} | Similarity: <strong>${item.similarity}</strong></div>
            </div>
        `;
    });
    container.innerHTML = html;
}

// Handle Natural Language Chat Form Submission
async function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    appendChatBubble('user', message);
    input.value = '';

    setLoading(true);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}`);
        }

        const data = await response.json();
        currentSessionId = data.session_id;

        let assistantMessage = data.message;
        if (!assistantMessage && data.reasoning_summary) {
            assistantMessage = data.reasoning_summary;
        }

        appendChatBubble('assistant', assistantMessage || 'Analysis complete.', data.recommendations);
        updateMetricsPanel(data.extracted_metrics);
        updateTracePanel(data.retrieval_trace);
    } catch (err) {
        appendChatBubble('assistant', `Server Communication Error: ${err.message}`);
    } finally {
        setLoading(false);
    }
}

// Handle Structured JSON Form Submission
async function handleJsonSubmit(event) {
    event.preventDefault();

    const metrics = {};

    const soc = document.getElementById('inputSoc').value.trim();
    const rainfall = document.getElementById('inputRainfall').value.trim();
    const landUse = document.getElementById('inputLandUse').value.trim();
    const region = document.getElementById('inputRegion').value;
    const ph = document.getElementById('inputPh').value.trim();
    const moisture = document.getElementById('inputMoisture').value.trim();
    const lat = document.getElementById('inputLat').value;
    const lon = document.getElementById('inputLon').value;
    const biodiversity = document.getElementById('inputBiodiversity').value.trim();
    const humanImpact = document.getElementById('inputHumanImpact').value.trim();

    if (soc) metrics['soil_organic_carbon'] = soc;
    if (rainfall) metrics['rainfall'] = rainfall;
    if (landUse) metrics['land_use'] = landUse;
    if (region) metrics['region_type'] = region;
    if (ph) metrics['soil_ph'] = ph;
    if (moisture) metrics['soil_moisture'] = moisture;
    if (lat) metrics['latitude'] = parseFloat(lat);
    if (lon) metrics['longitude'] = parseFloat(lon);
    if (biodiversity) metrics['biodiversity_indicators'] = biodiversity;
    if (humanImpact) metrics['human_impact'] = humanImpact;

    if (Object.keys(metrics).length === 0) {
        alert('Please fill out at least one environmental metric field.');
        return;
    }

    setLoading(true);

    try {
        const response = await fetch('/chat/json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                metrics: metrics
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}`);
        }

        const data = await response.json();
        currentSessionId = data.session_id;

        // Switch to Chat tab to present response
        switchMode('chat');

        appendChatBubble('user', `Submitted Structured Metrics Payload: ${JSON.stringify(metrics, null, 2)}`);
        appendChatBubble('assistant', data.reasoning_summary || data.message || 'Analysis complete.', data.recommendations);

        updateMetricsPanel(data.extracted_metrics);
        updateTracePanel(data.retrieval_trace);
    } catch (err) {
        alert(`Error submitting JSON payload: ${err.message}`);
    } finally {
        setLoading(false);
    }
}

// Fill sample PRD data into JSON form
function fillSampleData() {
    document.getElementById('inputSoc').value = '0.3%';
    document.getElementById('inputRainfall').value = 'low (400mm)';
    document.getElementById('inputLandUse').value = 'monoculture wheat';
    document.getElementById('inputRegion').value = 'semi-arid';
    document.getElementById('inputBiodiversity').value = 'declining beneficial insects & soil microflora';
}
