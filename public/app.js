/**
 * Shipmate Frontend Client Logic
 * Handles interactive developer workflow, backend API calls, deliverables formatting,
 * deep dives, copy/download actions, and session history.
 */

// Application State
let currentShipPack = null;
let currentCodeInput = "";
let currentInputType = "Git Diff";
let samplesData = { demo_change: null, samples: {} };
let sessionHistory = [];

// DOM Element References
const providerSelect = document.getElementById("providerSelect");
const providerCaption = document.getElementById("providerCaption");
const modelInput = document.getElementById("modelInput");
const apiKeyInput = document.getElementById("apiKeyInput");
const apiKeyStatus = document.getElementById("apiKeyStatus");
const sampleSelect = document.getElementById("sampleSelect");
const loadSampleBtn = document.getElementById("loadSampleBtn");
const historyContainer = document.getElementById("historyContainer");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");

const btnTryDemo = document.getElementById("btnTryDemo");
const btnClearInputs = document.getElementById("btnClearInputs");
const codeTextarea = document.getElementById("codeTextarea");
const contextInput = document.getElementById("contextInput");
const btnAnalyze = document.getElementById("btnAnalyze");
const statusBox = document.getElementById("statusBox");
const emptyState = document.getElementById("emptyState");
const resultsContainer = document.getElementById("resultsContainer");

// Metrics
const scoreNumber = document.getElementById("scoreNumber");
const scoreFactor = document.getElementById("scoreFactor");
const scoreBadgePill = document.getElementById("scoreBadgePill");
const riskBadge = document.getElementById("riskBadge");
const riskExplanation = document.getElementById("riskExplanation");
const testsCount = document.getElementById("testsCount");
const testsPriorityNote = document.getElementById("testsPriorityNote");
const readinessBadge = document.getElementById("readinessBadge");
const readinessReason = document.getElementById("readinessReason");

// Change Intelligence
const changeTypeBadge = document.getElementById("changeTypeBadge");
const whatChangedBody = document.getElementById("whatChangedBody");
const whyChangedBody = document.getElementById("whyChangedBody");

// Issues & Tests Containers
const issuesList = document.getElementById("issuesList");
const issuesCountBadge = document.getElementById("issuesCountBadge");
const testsList = document.getElementById("testsList");
const testsCountBadge = document.getElementById("testsCountBadge");

// ShipPack Deliverables
const managerContent = document.getElementById("managerContent");
const ticketContent = document.getElementById("ticketContent");
const techContent = document.getElementById("techContent");
const releaseContent = document.getElementById("releaseContent");
const rawMarkdownContent = document.getElementById("rawMarkdownContent");
const btnCopyShipPack = document.getElementById("btnCopyShipPack");
const btnDownloadShipPack = document.getElementById("btnDownloadShipPack");

// Toast
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toastMessage");

// Initialize on page load
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  loadHistoryFromStorage();
  await checkHealth();
  await loadSamples();
});

// Setup UI Event Listeners
function setupEventListeners() {
  // Provider Switcher
  providerSelect.addEventListener("change", () => {
    const provider = providerSelect.value;
    if (provider === "gemini") {
      modelInput.value = "gemini-1.5-flash";
      providerCaption.textContent = "Powered by Google Gemini 1.5 Flash (default).";
    } else if (provider === "openai") {
      modelInput.value = "gpt-4o-mini";
      providerCaption.textContent = "Powered by OpenAI GPT-4o-mini.";
    } else if (provider === "demo") {
      modelInput.value = "built-in-mock";
      providerCaption.textContent = "Built-in realistic mock analyzer for testing without an API key.";
    }
  });

  // Input Type Segmented Control
  const segmentBtns = document.querySelectorAll(".btn-segment");
  segmentBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      segmentBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentInputType = btn.getAttribute("data-type");
      updateInputLabels(currentInputType);
    });
  });

  // Try Demo Change (Payment Retry)
  btnTryDemo.addEventListener("click", () => {
    if (samplesData.demo_change) {
      codeTextarea.value = samplesData.demo_change.diff;
      contextInput.value = samplesData.demo_change.context;
      showToast("Loaded Payment Retry demo change");
      setWorkflowStep(1);
    }
  });

  // Clear Inputs
  btnClearInputs.addEventListener("click", () => {
    codeTextarea.value = "";
    contextInput.value = "";
    setWorkflowStep(1);
  });

  // Load Preset Sample
  loadSampleBtn.addEventListener("click", () => {
    const key = sampleSelect.value;
    if (key && samplesData.samples && samplesData.samples[key]) {
      const sample = samplesData.samples[key];
      codeTextarea.value = sample.diff;
      contextInput.value = sample.context || "";
      showToast(`Loaded sample: ${sample.title}`);
      setWorkflowStep(1);
    }
  });

  // Clear History
  clearHistoryBtn.addEventListener("click", () => {
    sessionHistory = [];
    localStorage.removeItem("shipmate_history");
    renderSessionHistory();
    showToast("Session history cleared");
  });

  // Analyze Change Button
  btnAnalyze.addEventListener("click", handleAnalyze);

  // ShipPack Action Buttons
  btnCopyShipPack.addEventListener("click", copyCompleteShipPack);
  btnDownloadShipPack.addEventListener("click", downloadShipPackMarkdown);

  // Tab Switching
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(tab => {
    tab.addEventListener("click", () => {
      tabBtns.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      const tabTarget = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
      
      if (tabTarget === "manager") document.getElementById("tabPaneManager").classList.add("active");
      if (tabTarget === "ticket") document.getElementById("tabPaneTicket").classList.add("active");
      if (tabTarget === "tech") document.getElementById("tabPaneTech").classList.add("active");
      if (tabTarget === "release") document.getElementById("tabPaneRelease").classList.add("active");
      if (tabTarget === "markdown") document.getElementById("tabPaneMarkdown").classList.add("active");
    });
  });

  // Generic Copy Buttons inside Tabs
  document.querySelectorAll(".copy-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        copyToClipboard(targetEl.textContent);
      }
    });
  });
}

function updateInputLabels(type) {
  const codeLabel = document.getElementById("codeLabel");
  if (type === "Code") {
    codeLabel.textContent = "Your Code (Source File / Snippet)";
    codeTextarea.placeholder = "Paste complete source code file or function to review...";
  } else {
    codeLabel.textContent = "Your Code Change (Git Diff / Patch)";
    codeTextarea.placeholder = "Paste your git diff or patch here (e.g. git diff origin/main)...";
  }
}

function setWorkflowStep(stepNum) {
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById(`flowStep${i}`);
    if (el) {
      if (i === stepNum) {
        el.classList.add("active");
      } else {
        el.classList.remove("active");
      }
    }
  }
}

// Health Check API
async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      if (data.has_gemini_key) {
        apiKeyStatus.innerHTML = "🔒 Server environment variable <code>GEMINI_API_KEY</code> is active and verified.";
      } else if (data.has_openai_key) {
        apiKeyStatus.innerHTML = "🔒 Server environment variable <code>OPENAI_API_KEY</code> is active and verified.";
      } else {
        apiKeyStatus.innerHTML = "⚠️ No server API key detected. Provide key above or use <strong>Demo Mode</strong>.";
        // Automatically default to demo mode if server has no key
        providerSelect.value = "demo";
        providerSelect.dispatchEvent(new Event("change"));
      }
    }
  } catch (err) {
    console.warn("Could not reach /api/health:", err);
  }
}

// Load Samples API
async function loadSamples() {
  try {
    const res = await fetch("/api/samples");
    if (res.ok) {
      samplesData = await res.json();
      if (samplesData.samples) {
        sampleSelect.innerHTML = '<option value="">-- Choose a sample diff --</option>';
        Object.entries(samplesData.samples).forEach(([key, val]) => {
          const opt = document.createElement("option");
          opt.value = key;
          opt.textContent = `${val.title} (${val.expected_risk} Risk)`;
          sampleSelect.appendChild(opt);
        });
      }
    }
  } catch (err) {
    console.warn("Could not load samples:", err);
  }
}

// Handle Analyze
async function handleAnalyze() {
  const code = codeTextarea.value.trim();
  const context = contextInput.value.trim();

  if (!code) {
    alert("Please paste a code change, git diff, or source snippet before analyzing.");
    codeTextarea.focus();
    return;
  }

  currentCodeInput = code;
  setWorkflowStep(2);
  emptyState.style.display = "none";
  resultsContainer.style.display = "none";
  statusBox.classList.add("active");
  btnAnalyze.disabled = true;
  btnAnalyze.textContent = "⏳ Analyzing Change...";

  // Progressive Status Animation
  const steps = [
    document.getElementById("step1"),
    document.getElementById("step2"),
    document.getElementById("step3"),
    document.getElementById("step4"),
    document.getElementById("step5")
  ];
  steps.forEach(s => {
    s.classList.remove("current", "done");
  });

  let currentStepIdx = 0;
  steps[0].classList.add("current");

  const intervalId = setInterval(() => {
    if (currentStepIdx < steps.length - 1) {
      steps[currentStepIdx].classList.remove("current");
      steps[currentStepIdx].classList.add("done");
      currentStepIdx++;
      steps[currentStepIdx].classList.add("current");
    }
  }, 1000);

  const payload = {
    code: code,
    context: context,
    input_type: currentInputType,
    provider: providerSelect.value,
    api_key: apiKeyInput.value.trim() || null,
    model: modelInput.value.trim() || null
  };

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    clearInterval(intervalId);
    steps.forEach(s => s.classList.add("done"));

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      const detail = errData.detail || `Server error (${res.status})`;
      throw new Error(detail);
    }

    const analysis = await res.json();
    currentShipPack = analysis;

    // Render analysis
    renderAnalysis(analysis);
    statusBox.classList.remove("active");
    resultsContainer.style.display = "block";
    showToast("ShipPack analysis ready!");

    // Save to session history
    addToHistory(analysis);

  } catch (err) {
    clearInterval(intervalId);
    statusBox.classList.remove("active");
    alert(`Analysis Failed:\n${err.message}`);
  } finally {
    btnAnalyze.disabled = false;
    btnAnalyze.textContent = "🚀 Analyze Change";
  }
}

// Render Analysis Dashboard
function renderAnalysis(data) {
  setWorkflowStep(5);
  // 1. Ship Score
  const score = data.ship_score !== undefined ? data.ship_score : 70;
  scoreNumber.textContent = score;
  scoreFactor.textContent = data.score_factor_explanation || data.ship_score_factor || "Calculated based on risk level and edge case coverage.";
  
  if (score >= 80) {
    scoreBadgePill.style.background = "var(--success-bg)";
    scoreBadgePill.style.color = "var(--success-text)";
    scoreBadgePill.textContent = "HIGH READINESS";
  } else if (score >= 50) {
    scoreBadgePill.style.background = "var(--warning-bg)";
    scoreBadgePill.style.color = "var(--warning-text)";
    scoreBadgePill.textContent = "REVIEW ADVISABLE";
  } else {
    scoreBadgePill.style.background = "var(--danger-bg)";
    scoreBadgePill.style.color = "var(--danger-text)";
    scoreBadgePill.textContent = "BLOCKERS DETECTED";
  }

  // 2. Risk Level
  const risk = (data.risk_level || "medium").toLowerCase();
  riskBadge.textContent = risk.toUpperCase();
  riskBadge.className = "";
  if (risk === "low") riskBadge.classList.add("risk-pill-low");
  else if (risk === "high") riskBadge.classList.add("risk-pill-high");
  else riskBadge.classList.add("risk-pill-medium");

  riskExplanation.textContent = data.risk_explanation || "Assessed based on behavioral changes.";

  // 3. Recommended Tests
  const tests = data.test_scenarios || [];
  testsCount.textContent = tests.length;
  const p0Count = tests.filter(t => (t.priority || "").toLowerCase() === "high").length;
  testsPriorityNote.textContent = p0Count > 0 ? `${p0Count} High Priority Tests` : "Prioritized by impact";

  // 4. Shipping Readiness
  const readiness = (data.shipping_readiness || "review recommended").toLowerCase();
  readinessBadge.textContent = readiness.toUpperCase();
  readinessBadge.className = "";
  if (readiness === "ready") {
    readinessBadge.classList.add("badge-ready");
  } else if (readiness.includes("not")) {
    readinessBadge.classList.add("badge-blocked");
  } else {
    readinessBadge.classList.add("badge-review");
  }
  readinessReason.textContent = data.readiness_reason || "Advisory based on risk factors.";

  // 5. Change Intelligence
  changeTypeBadge.textContent = data.change_type || "Feature";
  whatChangedBody.textContent = data.change_summary || "No summary provided.";
  whyChangedBody.textContent = data.change_purpose || "No change purpose provided.";

  // 6. Potential Issues List
  renderIssues(data.potential_issues || []);

  // 7. Recommended Tests List
  renderTests(data.test_scenarios || []);

  // 8. ShipPack Deliverables
  managerContent.textContent = data.manager_update || "";
  ticketContent.textContent = data.ticket_update || "";
  techContent.textContent = data.technical_documentation || "";
  releaseContent.textContent = data.release_notes || "";
  rawMarkdownContent.textContent = buildCompleteShipPackMarkdown(data);
}

// Render Potential Issues with "Explain, suggest a fix"
function renderIssues(issues) {
  issuesList.innerHTML = "";
  issuesCountBadge.textContent = `(${issues.length} detected)`;

  if (issues.length === 0) {
    issuesList.innerHTML = `
      <div style="padding: 1rem; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; color: var(--success-text); font-size: 0.9rem;">
        ✓ No high-severity potential issues or edge cases detected in this change.
      </div>
    `;
    return;
  }

  issues.forEach((issue, index) => {
    const sev = (issue.severity || "medium").toLowerCase();
    const card = document.createElement("div");
    card.className = `issue-card issue-card-${sev}`;

    const sevPillClass = sev === "high" ? "risk-pill-high" : (sev === "low" ? "risk-pill-low" : "risk-pill-medium");

    card.innerHTML = `
      <div class="issue-header-row">
        <div class="issue-title">${escapeHtml(issue.title)}</div>
        <span class="${sevPillClass}">${sev.toUpperCase()}</span>
      </div>
      <div class="issue-explanation">${escapeHtml(issue.explanation)}</div>
      <div class="issue-action-box">
        <strong>Suggested Action:</strong> ${escapeHtml(issue.suggested_action)}
      </div>
      <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
        <button type="button" class="btn btn-secondary btn-sm deep-dive-btn" data-index="${index}">
          🔍 Explain, suggest a fix
        </button>
      </div>
      <div class="deep-dive-card" id="deepDiveCard_${index}">
        <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 0.65rem; color: var(--text-main);">
          🛠️ Architectural Deep Dive &amp; Fix
        </div>
        <div class="deep-dive-section">
          <div class="deep-dive-label">Why This Matters</div>
          <div class="deep-dive-text" id="deepDiveWhy_${index}">Loading...</div>
        </div>
        <div class="deep-dive-section">
          <div class="deep-dive-label">Where It Occurs</div>
          <div class="deep-dive-text" id="deepDiveWhere_${index}">Loading...</div>
        </div>
        <div class="deep-dive-section">
          <div class="deep-dive-label">Recommended Approach</div>
          <div class="deep-dive-text" id="deepDiveRec_${index}">Loading...</div>
        </div>
        <div class="deep-dive-section" id="deepDiveFixSection_${index}" style="display: none;">
          <div class="deep-dive-label">Suggested Code Fix</div>
          <div class="code-box" id="deepDiveFix_${index}"></div>
        </div>
      </div>
    `;

    // Hook up Deep Dive button
    const ddBtn = card.querySelector(".deep-dive-btn");
    ddBtn.addEventListener("click", () => handleDeepDive(issue, index, ddBtn));

    issuesList.appendChild(card);
  });
}

// Handle Deep Dive on an Issue
async function handleDeepDive(issue, index, btn) {
  const card = document.getElementById(`deepDiveCard_${index}`);
  if (card.classList.contains("open")) {
    card.classList.remove("open");
    btn.textContent = "🔍 Explain, suggest a fix";
    return;
  }

  card.classList.add("open");
  btn.textContent = "⏳ Generating fix advice...";
  btn.disabled = true;

  try {
    const res = await fetch("/api/deep-dive", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: currentCodeInput,
        issue: issue,
        provider: providerSelect.value,
        api_key: apiKeyInput.value.trim() || null,
        model: modelInput.value.trim() || null
      })
    });

    if (!res.ok) {
      throw new Error(`Failed to load fix: ${res.status}`);
    }

    const dive = await res.json();
    document.getElementById(`deepDiveWhy_${index}`).textContent = dive.why_this_matters || "Identified as a critical stability factor.";
    document.getElementById(`deepDiveWhere_${index}`).textContent = dive.where_problem_occurs || "Affects data flow within the modified logic.";
    document.getElementById(`deepDiveRec_${index}`).textContent = dive.recommended_approach || "Add targeted guardrails and validate inputs.";

    const fixSection = document.getElementById(`deepDiveFixSection_${index}`);
    const fixCode = document.getElementById(`deepDiveFix_${index}`);
    const codeSnippet = dive.example_fix_code || dive.example_fix;
    if (codeSnippet) {
      fixCode.textContent = codeSnippet;
      fixSection.style.display = "block";
    } else {
      fixSection.style.display = "none";
    }

    btn.textContent = "Hide fix advice";
    btn.disabled = false;
  } catch (err) {
    document.getElementById(`deepDiveWhy_${index}`).textContent = "Could not generate fix advice at this time.";
    btn.textContent = "Explain, suggest a fix";
    btn.disabled = false;
  }
}

// Render Recommended Tests
function renderTests(tests) {
  testsList.innerHTML = "";
  testsCountBadge.textContent = `(${tests.length} recommended)`;

  if (tests.length === 0) {
    testsList.innerHTML = `
      <div style="padding: 1rem; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-muted); font-size: 0.9rem;">
        No specific test scenarios generated.
      </div>
    `;
    return;
  }

  tests.forEach(test => {
    const card = document.createElement("div");
    card.className = "test-card";
    const pri = (test.priority || "medium").toUpperCase();
    const priClass = pri === "HIGH" ? "risk-pill-high" : (pri === "LOW" ? "risk-pill-low" : "risk-pill-medium");
    const name = test.test_name || test.name || "Test Scenario";
    const desc = test.test_description || test.description || "";

    card.innerHTML = `
      <div class="test-header-row">
        <div class="test-title">${escapeHtml(name)}</div>
        <span class="${priClass}">${pri}</span>
      </div>
      <div class="test-desc">${escapeHtml(desc)}</div>
    `;
    testsList.appendChild(card);
  });
}

// Build Complete ShipPack Markdown string
function buildCompleteShipPackMarkdown(analysis) {
  const dateStr = new Date().toISOString().split("T")[0];
  const issuesMd = (analysis.potential_issues || []).map(i => 
    `- **[${(i.severity || "MED").toUpperCase()}] ${i.title}**: ${i.explanation}\n  *Action*: ${i.suggested_action}`
  ).join("\n");

  const testsMd = (analysis.test_scenarios || []).map(t => {
    const name = t.test_name || t.name || "Test Scenario";
    const desc = t.test_description || t.description || "";
    return `- [${(t.priority || "MED").toUpperCase()}] **${name}**: ${desc}`;
  }).join("\n");

  return `# ShipMate Release Pack
*Generated on ${dateStr} by ShipMate*

## 1. Executive Summary
- **Ship Score**: ${analysis.ship_score !== undefined ? analysis.ship_score : 70}/100 (${analysis.score_factor_explanation || analysis.ship_score_factor || "AI Assessment"})
- **Risk Level**: ${(analysis.risk_level || "MEDIUM").toUpperCase()} — ${analysis.risk_explanation || ""}
- **Shipping Readiness**: ${(analysis.shipping_readiness || "REVIEW RECOMMENDED").toUpperCase()} — ${analysis.readiness_reason || ""}
- **Change Type**: ${analysis.change_type || "Feature"}

## 2. Change Intelligence
### What Changed
${analysis.change_summary || "N/A"}

### Why It Changed
${analysis.change_purpose || "N/A"}

## 3. Potential Issues & Edge Cases
${issuesMd || "No high-severity issues detected."}

## 4. Recommended Test Plan
${testsMd || "Standard regression testing recommended."}

---

## 5. Ready-to-Send Deliverables

### Manager Update (Stakeholder Briefing)
\`\`\`
${analysis.manager_update || ""}
\`\`\`

### Ticket Update (Jira / Linear / Issue)
\`\`\`
${analysis.ticket_update || ""}
\`\`\`

### Technical Documentation
\`\`\`
${analysis.technical_documentation || ""}
\`\`\`

### Release Notes (User / System Impact)
\`\`\`
${analysis.release_notes || ""}
\`\`\`
`;
}

// Copy Complete ShipPack
function copyCompleteShipPack() {
  if (!currentShipPack) return;
  const md = buildCompleteShipPackMarkdown(currentShipPack);
  copyToClipboard(md, "Complete ShipPack copied to clipboard!");
}

// Download ShipPack Markdown file
function downloadShipPackMarkdown() {
  if (!currentShipPack) return;
  const md = buildCompleteShipPackMarkdown(currentShipPack);
  const title = (currentShipPack.change_type || "shippack").toLowerCase().replace(/[^a-z0-9]/g, "_");
  const filename = `shippack_${title}_${Date.now()}.md`;

  const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast(`Downloaded ${filename}`);
}

// Clipboard Helper
function copyToClipboard(text, customMsg) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(customMsg || "Copied to clipboard!");
    }).catch(() => {
      fallbackCopy(text, customMsg);
    });
  } else {
    fallbackCopy(text, customMsg);
  }
}

function fallbackCopy(text, customMsg) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.left = "-9999px";
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try {
    document.execCommand("copy");
    showToast(customMsg || "Copied to clipboard!");
  } catch (err) {
    alert("Could not copy automatically. Please copy manually.");
  }
  document.body.removeChild(ta);
}

// Toast Feedback Helper
let toastTimer = null;
function showToast(msg) {
  toastMessage.textContent = msg;
  toast.classList.add("show");
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2400);
}

// History Management
function addToHistory(analysis) {
  const item = {
    id: Date.now(),
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    type: analysis.change_type || "Change",
    score: analysis.ship_score !== undefined ? analysis.ship_score : 70,
    risk: (analysis.risk_level || "MED").toUpperCase(),
    summary: (analysis.change_summary || "").slice(0, 75) + "...",
    fullAnalysis: analysis,
    codeInput: currentCodeInput
  };

  sessionHistory.unshift(item);
  if (sessionHistory.length > 8) sessionHistory.pop();

  saveHistoryToStorage();
  renderSessionHistory();
}

function saveHistoryToStorage() {
  try {
    localStorage.setItem("shipmate_history", JSON.stringify(sessionHistory));
  } catch (err) {
    // Quota or disabled localStorage
  }
}

function loadHistoryFromStorage() {
  try {
    const raw = localStorage.getItem("shipmate_history");
    if (raw) {
      sessionHistory = JSON.parse(raw);
      renderSessionHistory();
    }
  } catch (err) {
    sessionHistory = [];
  }
}

function renderSessionHistory() {
  if (!historyContainer) return;

  if (sessionHistory.length === 0) {
    historyContainer.innerHTML = '<div style="font-size: 0.8rem; color: var(--text-muted); font-style: italic;">No analyses in this session yet.</div>';
    return;
  }

  historyContainer.innerHTML = "";
  sessionHistory.forEach(item => {
    const el = document.createElement("div");
    el.className = "history-item";
    el.innerHTML = `
      <div class="history-item-top">
        <span>${escapeHtml(item.type)} (${item.score}/100)</span>
        <span style="font-size: 0.72rem; color: var(--text-muted);">${item.timestamp}</span>
      </div>
      <div class="history-item-summary">${escapeHtml(item.summary)}</div>
      <button type="button" class="btn btn-secondary btn-sm" style="width: 100%; padding: 0.2rem 0.5rem; font-size: 0.74rem;">
        Reopen
      </button>
    `;

    el.querySelector("button").addEventListener("click", () => {
      currentShipPack = item.fullAnalysis;
      currentCodeInput = item.codeInput;
      codeTextarea.value = item.codeInput;
      emptyState.style.display = "none";
      renderAnalysis(item.fullAnalysis);
      resultsContainer.style.display = "block";
      showToast("Reopened previous analysis");
    });

    historyContainer.appendChild(el);
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
