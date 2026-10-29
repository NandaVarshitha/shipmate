# 🚢 Shipmate: AI-Powered Developer Shipping Assistant

> **From Code Change to Ship Pack in Seconds.**  
> Paste a git diff once. Shipmate generates risk evaluations, bug hunting scenarios, test matrices, manager updates, ticket markdown, technical docs, release notes, and a definitive shipping readiness verdict.

---

## 🎯 The Problem
When developers finish writing code, coding is often only half the job. Before shipping, developers spend 30–60+ minutes:
1. Explaining the change to non-technical managers on Slack or Teams.
2. Writing PR descriptions and updating Jira/Linear tickets.
3. Brainstorming edge-cases and manual test scenarios.
4. Assessing blast radius, breaking changes, and risk.
5. Updating architecture/API documentation.
6. Drafting customer-facing release notes.

**Shipmate solves this.** Developers paste their `git diff` once, and Shipmate's Staff-level AI generates a comprehensive, structured **Ship Pack**.

---

## 📦 What's Inside a Ship Pack?
Every analysis produces 9 synchronized deliverables:
1. **Simple Explanation & Rationale**: What changed and the root problem being solved.
2. **Risk Analysis**: Blast radius, breaking changes, and a quantified 0–100 risk index.
3. **Potential Bugs & Edge Cases**: Pinpoints race conditions, timeout vulnerabilities, unhandled errors, and actionable mitigations.
4. **Recommended Test Scenarios**: Categorized into Unit Tests, Integration Tests, Manual QA, and Chaos/Edge-cases with step-by-step verification instructions.
5. **Manager-Friendly Status Update**: Executive summary and business impact written for non-technical stakeholders.
6. **Ticket Update**: Ready-to-paste markdown formatted for Jira, Linear, or GitHub PR descriptions, complete with pre-merge checklists.
7. **Technical Documentation**: Architecture notes, API/contract changes, and maintainer gotchas.
8. **Release Notes**: Dual-track output — customer-facing changelog highlights + internal developer logs.
9. **Shipping Readiness Verdict**: Clear decision badge (`READY_TO_SHIP`, `NEEDS_TESTING`, `NEEDS_SENIOR_REVIEW`, `BLOCKED`) with confidence score.

---

## 🏗️ Project Architecture
```
shipmate/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python package dependencies
├── README.md                 # Project documentation and quickstart
├── app.py                    # Streamlit application entrypoint
└── src/
    ├── __init__.py
    ├── config.py             # Settings, defaults, and environment loading
    ├── models.py             # Pydantic v2 schemas enforcing strict JSON outputs
    ├── prompts.py            # Prompt engineering and system instructions
    ├── sample_diffs.py       # Realistic git diffs for instant 1-click demos
    ├── services/
    │   ├── __init__.py
    │   ├── llm_provider.py   # Multi-provider client (Gemini REST, OpenAI, Demo/Mock)
    │   └── analyzer.py       # Orchestration layer and response validation
    └── ui/
        ├── __init__.py
        ├── styles.py         # Modern CSS styles (clean typography, badges, pills)
        └── components.py     # Streamlit UI renderers (Readiness hero, tab views, export)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.8+
- (Optional) A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/) or OpenAI API key.

### 2. Install Dependencies
```bash
cd shipmate
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```
> *Note: If no API key is provided, Shipmate runs seamlessly in **Demo Mode**, generating high-fidelity simulated Ship Packs from curated real-world diffs.*

### 4. Run the Streamlit App
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## ⚡ Hackathon Presentation Tip
Shipmate includes **3 built-in realistic sample diffs** in the sidebar:
- **Auth Race Condition**: Double-checked locking and token refresh storm fix.
- **Stripe Webhook Idempotency**: Payment transaction wrapping and duplicate event prevention.
- **Database Connection Pooling**: SQLAlchemy connection recycle and pre-ping resilience.

Click **"Load Sample into Editor"** and hit **"🚀 Generate Ship Pack"** for an instant, show-stopping live demo!
