// In-memory Session UUID state (persists across turns during page life)
let currentSessionId = null;
let currentMode = 'chat';

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

// Format recommendations as distinct scannable cards
function renderRecommendationsHTML(recs) {
    if (!recs || recs.length === 0) return '';

    let html = '<div style="margin-top: 1rem; font-weight:600; color:var(--accent-mint);">Substantive Evidence-Backed Interventions:</div>';

    recs.forEach((rec, idx) => {
        const metricsBadges = (rec.impacted_metrics || []).map(m => `<span class="badge badge-metric">${m}</span>`).join(' ');

        html += `
            <div class="recommendation-card">
                <div class="rec-title">
                    <span>🌱 Intervention ${idx + 1}:</span> ${escapeHTML(rec.intervention)}
                </div>
                <div class="rec-mechanism">
                    <strong>Scientific Mechanism:</strong> ${escapeHTML(rec.mechanism)}
                </div>
                <div class="rec-badges">
                    ${metricsBadges}
                    <span class="badge badge-improvement">📈 ${escapeHTML(rec.expected_improvement || 'Quantified Restoration')}</span>
                    <span class="badge badge-horizon">⏳ ${escapeHTML(rec.time_horizon || 'medium')} term</span>
                </div>
                <div class="rec-citation">
                    <span>📖 Source Citation:</span> ${escapeHTML(rec.citation)} (Confidence: ${escapeHTML(rec.confidence || 'high')})
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
    const avatar = isAssistant ? '🌱' : '👤';
    const sender = isAssistant ? 'AI Environmental Scientist' : 'You';

    let bodyHTML = escapeHTML(text);

    if (recommendations && recommendations.length > 0) {
        bodyHTML += renderRecommendationsHTML(recommendations);
    }

    bubble.innerHTML = `
        <div class="bubble-header">
            <span class="bubble-avatar">${avatar}</span>
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
        container.innerHTML = '<span class="empty-state-text">No metrics extracted yet.</span>';
        return;
    }

    let html = '';
    for (const [key, val] of Object.entries(metrics)) {
        if (val) {
            html += `<div class="metric-tag"><strong>${escapeHTML(key)}:</strong> ${escapeHTML(String(val))}</div>`;
        }
    }
    container.innerHTML = html;
}

// Update Retrieval Trace Panel
function updateTracePanel(trace) {
    const container = document.getElementById('traceFeed');
    if (!trace || trace.length === 0) {
        container.innerHTML = '<span class="empty-state-text">Retrieved knowledge chunks will appear here upon submission.</span>';
        return;
    }

    let html = '';
    trace.forEach(item => {
        html += `
            <div class="trace-item">
                <div class="trace-item-title">${escapeHTML(item.source_title || 'Reference Chunk')}</div>
                <div class="trace-item-meta">Category: ${escapeHTML(item.category || 'general')} | Cosine Similarity: <strong>${item.similarity}</strong></div>
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
        appendChatBubble('assistant', `⚠️ Error communicating with server: ${err.message}`);
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

        appendChatBubble('user', `Submitted Structured Metrics: ${JSON.stringify(metrics, null, 2)}`);
        appendChatBubble('assistant', data.reasoning_summary || data.message || 'Analysis complete.', data.recommendations);

        updateMetricsPanel(data.extracted_metrics);
        updateTracePanel(data.retrieval_trace);
    } catch (err) {
        alert(`⚠️ Error submitting JSON payload: ${err.message}`);
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

function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
