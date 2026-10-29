"""
Professional, minimal, and responsive developer tool CSS styling for Shipmate.
"""

CUSTOM_CSS = """
<style>
/* Modern typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

code, pre, .stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
}

/* App Header / Hero Section */
.shipmate-hero {
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 1.5rem;
}

@media (prefers-color-scheme: dark) {
    .shipmate-hero {
        border-bottom-color: #334155;
    }
}

.shipmate-title-row {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    margin-bottom: 0.4rem;
}

.shipmate-brand-title {
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 0;
    line-height: 1.2;
}

.shipmate-flow-badge {
    display: inline-block;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.2rem 0.65rem;
    border-radius: 9999px;
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
}

@media (prefers-color-scheme: dark) {
    .shipmate-flow-badge {
        background: #1e293b;
        color: #94a3b8;
        border-color: #334155;
    }
}

.shipmate-description {
    font-size: 0.95rem;
    color: #64748b;
    margin: 0;
    max-width: 780px;
    line-height: 1.5;
}

@media (prefers-color-scheme: dark) {
    .shipmate-description {
        color: #94a3b8;
    }
}

/* Empty State Container */
.shipmate-empty-state {
    text-align: center;
    padding: 3rem 1.5rem;
    margin-top: 1.5rem;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    background: #fafafa;
}

@media (prefers-color-scheme: dark) {
    .shipmate-empty-state {
        border-color: #334155;
        background: #0f172a;
    }
}

.empty-state-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #334155;
    margin-bottom: 0.5rem;
}

@media (prefers-color-scheme: dark) {
    .empty-state-title {
        color: #f1f5f9;
    }
}

.empty-state-desc {
    font-size: 0.9rem;
    color: #64748b;
    max-width: 580px;
    margin: 0 auto 1.5rem auto;
    line-height: 1.5;
}

@media (prefers-color-scheme: dark) {
    .empty-state-desc {
        color: #94a3b8;
    }
}

.empty-state-features {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.empty-feature-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8rem;
    color: #475569;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-weight: 500;
}

@media (prefers-color-scheme: dark) {
    .empty-feature-item {
        background: #1e293b;
        border-color: #334155;
        color: #cbd5e1;
    }
}

/* ==============================================================================
   POLISHED SHIPMENT DASHBOARD STYLING
   ============================================================================== */

/* Summary Metric Cards */
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    height: 100%;
}

@media (prefers-color-scheme: dark) {
    .metric-card {
        background: #1e293b;
        border-color: #334155;
    }
}

.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    margin-bottom: 0.35rem;
}

@media (prefers-color-scheme: dark) {
    .metric-label {
        color: #94a3b8;
    }
}

.metric-value-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.metric-main-value {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0;
}

.metric-caption {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.35rem;
    line-height: 1.35;
}

@media (prefers-color-scheme: dark) {
    .metric-caption {
        color: #94a3b8;
    }
}

/* Clean Status & Verdict Badges */
.badge-ready {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
    padding: 0.28rem 0.75rem;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.82rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

.badge-review {
    background: #fffbeb;
    color: #92400e;
    border: 1px solid #fde68a;
    padding: 0.28rem 0.75rem;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.82rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

.badge-blocked {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
    padding: 0.28rem 0.75rem;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.82rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

.risk-pill-low {
    background: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.95rem;
}

.risk-pill-medium {
    background: #fffbeb;
    color: #b45309;
    border: 1px solid #fde68a;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.95rem;
}

.risk-pill-high {
    background: #fef2f2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-weight: 800;
    font-size: 0.95rem;
}

/* ==============================================================================
   CHANGE INTELLIGENCE SECTION
   ============================================================================== */
.intel-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.25rem 1.4rem;
    margin: 1.25rem 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

@media (prefers-color-scheme: dark) {
    .intel-container {
        background: #1e293b;
        border-color: #334155;
    }
}

.intel-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.85rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid #f1f5f9;
}

@media (prefers-color-scheme: dark) {
    .intel-heading {
        border-bottom-color: #334155;
    }
}

.intel-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin: 0;
    color: #0f172a;
}

@media (prefers-color-scheme: dark) {
    .intel-title {
        color: #f8fafc;
    }
}

.intel-content-box {
    background: #f8fafc;
    border-left: 3px solid #3b82f6;
    padding: 0.85rem 1.1rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.92rem;
    line-height: 1.55;
    color: #334155;
    margin-top: 0.4rem;
}

@media (prefers-color-scheme: dark) {
    .intel-content-box {
        background: #0f172a;
        border-left-color: #60a5fa;
        color: #cbd5e1;
    }
}

/* ==============================================================================
   POTENTIAL ISSUES (PROMINENCE HIERARCHY)
   ============================================================================== */
.issue-card {
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    transition: transform 0.1s ease;
}

/* High Severity: Noticeably Prominent with Red Left Border & Soft Crimson Wash */
.issue-card-high {
    border: 1px solid #fca5a5;
    border-left: 5px solid #dc2626;
    background: #fffafa;
}

@media (prefers-color-scheme: dark) {
    .issue-card-high {
        border-color: #7f1d1d;
        border-left: 5px solid #ef4444;
        background: #1f1214;
    }
}

/* Medium Severity: Balanced Amber Alert */
.issue-card-medium {
    border: 1px solid #fde68a;
    border-left: 4px solid #d97706;
    background: #fffdf7;
}

@media (prefers-color-scheme: dark) {
    .issue-card-medium {
        border-color: #78350f;
        border-left: 4px solid #f59e0b;
        background: #1f1a12;
    }
}

/* Low Severity: Subtle Neutral Card */
.issue-card-low {
    border: 1px solid #e2e8f0;
    border-left: 3px solid #64748b;
    background: #fafafa;
}

@media (prefers-color-scheme: dark) {
    .issue-card-low {
        border-color: #334155;
        border-left: 3px solid #94a3b8;
        background: #182234;
    }
}

.issue-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}

.issue-title-text {
    font-size: 0.98rem;
    font-weight: 600;
    margin: 0;
    color: #0f172a;
}

@media (prefers-color-scheme: dark) {
    .issue-title-text {
        color: #f8fafc;
    }
}

.issue-sev-badge-high {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
}

.issue-sev-badge-med {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
}

.issue-sev-badge-low {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
}

.issue-explanation-body {
    font-size: 0.9rem;
    line-height: 1.55;
    color: #334155;
    margin-bottom: 0.65rem;
}

@media (prefers-color-scheme: dark) {
    .issue-explanation-body {
        color: #cbd5e1;
    }
}

.issue-action-pill {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    font-size: 0.84rem;
    line-height: 1.45;
    color: #0f172a;
}

@media (prefers-color-scheme: dark) {
    .issue-action-pill {
        background: #0f172a;
        border-color: #334155;
        color: #e2e8f0;
    }
}

/* ==============================================================================
   RECOMMENDED TESTS SECTION
   ============================================================================== */
.test-item-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

@media (prefers-color-scheme: dark) {
    .test-item-card {
        background: #1e293b;
        border-color: #334155;
    }
}

.test-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.test-title-text {
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0;
    color: #0f172a;
}

@media (prefers-color-scheme: dark) {
    .test-title-text {
        color: #f8fafc;
    }
}

.test-desc-text {
    font-size: 0.88rem;
    line-height: 1.5;
    color: #475569;
}

@media (prefers-color-scheme: dark) {
    .test-desc-text {
        color: #94a3b8;
    }
}

/* ==============================================================================
   SHIPPACK DELIVERABLES SECTION
   ============================================================================== */
.shippack-section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

@media (prefers-color-scheme: dark) {
    .shippack-section-header {
        color: #f8fafc;
    }
}

.memo-box {
    background: #f8fafc;
    border-left: 3px solid #6366f1;
    padding: 1.1rem 1.3rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.92rem;
    line-height: 1.6;
    color: #1e293b;
    margin: 0.75rem 0;
}

@media (prefers-color-scheme: dark) {
    .memo-box {
        background: #0f172a;
        border-left-color: #818cf8;
        color: #e2e8f0;
    }
}

/* Subtle Metadata Tag */
.meta-tag {
    display: inline-block;
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 0.2rem 0.5rem;
    font-size: 0.76rem;
    font-weight: 600;
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
}

@media (prefers-color-scheme: dark) {
    .meta-tag {
        background: #1e293b;
        color: #94a3b8;
        border-color: #334155;
    }
}
/* Interactive Issue Deep Dive & Fix Advisory */
.deep-dive-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    margin-top: 0.85rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

@media (prefers-color-scheme: dark) {
    .deep-dive-card {
        background: #131c2e;
        border-color: #334155;
    }
}

.deep-dive-section {
    margin-bottom: 0.85rem;
}

.deep-dive-section:last-child {
    margin-bottom: 0;
}

.deep-dive-label {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #64748b;
    margin-bottom: 0.25rem;
}

@media (prefers-color-scheme: dark) {
    .deep-dive-label {
        color: #94a3b8;
    }
}

.deep-dive-text {
    font-size: 0.9rem;
    line-height: 1.55;
    color: #1e293b;
}

@media (prefers-color-scheme: dark) {
    .deep-dive-text {
        color: #e2e8f0;
    }
}

.fix-advisory-note {
    font-size: 0.78rem;
    color: #64748b;
    font-style: italic;
    margin-top: 0.35rem;
}

@media (prefers-color-scheme: dark) {
    .fix-advisory-note {
        color: #94a3b8;
    }
}

.context-missing-box {
    background: #fffbeb;
    border-left: 3px solid #f59e0b;
    padding: 0.85rem 1.1rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.88rem;
    color: #92400e;
    line-height: 1.5;
}

/* Flow Steps */
.shipmate-flow-steps {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    flex-wrap: wrap;
}

.shipmate-flow-steps span {
    background: #f1f5f9;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}

.shipmate-flow-steps .step-ship {
    background: #ecfdf5;
    color: #065f46;
    border-color: #a7f3d0;
    font-weight: 700;
}

@media (prefers-color-scheme: dark) {
    .shipmate-flow-steps span {
        background: #1e293b;
        border-color: #334155;
        color: #94a3b8;
    }
    .shipmate-flow-steps .step-ship {
        background: #064e3b;
        color: #6ee7b7;
        border-color: #047857;
    }
}

/* Ship Score Card */
.score-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    height: 100%;
    position: relative;
    border-top: 3px solid #3b82f6;
}

@media (prefers-color-scheme: dark) {
    .score-card {
        background: #1e293b;
        border-color: #334155;
        border-top-color: #60a5fa;
    }
}

.score-display-row {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-top: 0.2rem;
}

.score-large-number {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
}

.score-max-scale {
    font-size: 1rem;
    font-weight: 600;
    color: #94a3b8;
}

.score-badge-pill {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    margin-bottom: 0.35rem;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}

@media (prefers-color-scheme: dark) {
    .score-badge-pill {
        background: #1e3a8a;
        color: #93c5fd;
        border-color: #2563eb;
    }
}

.score-factor-text {
    font-size: 0.82rem;
    color: #334155;
    margin-top: 0.5rem;
    line-height: 1.45;
    padding-top: 0.45rem;
    border-top: 1px dashed #e2e8f0;
}

@media (prefers-color-scheme: dark) {
    .score-factor-text {
        color: #cbd5e1;
        border-top-color: #334155;
    }
}

.score-disclaimer {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 0.35rem;
    font-style: italic;
    line-height: 1.35;
}

/* History Card in Sidebar */
.history-item {
    padding: 0.5rem 0.65rem;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background: #ffffff;
    margin-bottom: 0.5rem;
}

@media (prefers-color-scheme: dark) {
    .history-item {
        background: #1e293b;
        border-color: #334155;
    }
}

/* Copy Action Bar */
.copy-action-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
    gap: 0.5rem;
}

.copy-subtitle {
    font-size: 0.85rem;
    color: #64748b;
}

@media (prefers-color-scheme: dark) {
    .copy-subtitle {
        color: #94a3b8;
    }
}
</style>
"""
