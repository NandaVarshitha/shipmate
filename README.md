# 🚢 ShipMate: Code Change → Ready to Ship

> **Turn any code change into a ready-to-ship package.**  
> ShipMate reviews your change, identifies potential risks, recommends tests, and generates the updates and documentation you need to ship.

---

## 🎯 The Problem
When developers finish writing code, coding is often only half the job. Before shipping, developers spend 30–60+ minutes:
1. Explaining the change to non-technical managers on Slack or Teams.
2. Writing PR descriptions and updating Jira/Linear tickets.
3. Brainstorming edge-cases and manual test scenarios.
4. Assessing blast radius, breaking changes, and risk.
5. Updating architecture/API documentation.
6. Drafting customer-facing release notes.

**ShipMate solves this.** Developers paste their code change once, and ShipMate's AI-assisted code risk assessment generates a comprehensive, structured **Ship Pack**.

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

## 🏗️ Project Architecture & Vercel Deployment Model
Shipmate uses a modern decoupled architecture optimized for **Vercel Serverless Functions**:
- **Backend API (`api/index.py`)**: Lightweight FastAPI serverless application serving `/api/analyze`, `/api/deep-dive`, `/api/samples`, and `/api/health`.
- **Frontend (`public/`)**: Modern vanilla HTML/CSS/JavaScript with responsive layout, zero compilation overhead, dynamic progress loading, and instant copy/download.
- **AI Core (`src/`)**: Pydantic models (`src/models.py`), LLM service (`src/services/llm_service.py`), and prompts (`src/prompts.py`).

```
shipmate/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules (protects keys and .env)
├── vercel.json               # Vercel serverless routing configuration
├── requirements.txt          # Python serverless dependencies (FastAPI, Pydantic, etc.)
├── README.md                 # Project documentation
├── api/
│   └── index.py              # FastAPI serverless entrypoint for Vercel (/api/*)
├── public/
│   ├── index.html            # Modern developer tool web interface
│   ├── styles.css            # Custom CSS design system (dark/light theme)
│   └── app.js                # Frontend client logic & interactive features
└── src/
    ├── config.py             # Settings and safe environment variable loader
    ├── models.py             # Pydantic v2 validation models
    ├── prompts.py            # Senior staff-level prompt engineering
    ├── sample_diffs.py       # Curated real-world git diffs
    └── services/
        ├── llm_service.py    # Multi-provider LLM service (Gemini, OpenAI, Demo)
        └── exceptions.py     # Custom error hierarchy
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
> *Note: If no API key is configured, Shipmate runs seamlessly in **Demo Mode**, generating high-fidelity simulated Ship Packs from curated real-world diffs.*

### 4. Run Locally
```bash
python -m uvicorn api.index:app --port 8000 --reload
```
Open your browser to `http://127.0.0.1:8000`.

---

## ☁️ Deploy to Vercel

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Deploy Shipmate to Vercel"
   git push origin main
   ```
2. Import the repository in [Vercel](https://vercel.com/new).
3. Under **Project Settings → Environment Variables**, add:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
4. Click **Deploy**. Vercel will automatically build the static assets and deploy the FastAPI serverless functions in `api/index.py`!

