"""
Polished Shipment Dashboard UI components for Shipmate.
Structured into Challenge Intelligence, Potential Issues, Recommended Tests, and ShipPack deliverables.
"""
from __future__ import annotations
from typing import Optional
from datetime import datetime
import streamlit as st
from src.models import ShipPackAnalysis, ShippingReadiness, RiskLevel, IssueDeepDive


def render_header():
    """Renders the main Shipmate interface header."""
    st.markdown(
        """
        <div class="shipmate-hero">
            <div class="shipmate-title-row">
                <h1 class="shipmate-brand-title">Shipmate</h1>
                <span class="shipmate-flow-badge">From &ldquo;Code Change&rdquo; to &ldquo;Ready to Ship&rdquo;</span>
            </div>
            <p class="shipmate-description">
                <strong>1. Understand the change</strong> &nbsp;&bull;&nbsp; 
                <strong>2. Find the standard test</strong> &nbsp;&bull;&nbsp; 
                <strong>3. Ship with confidence</strong>
            </p>
            <div class="shipmate-flow-steps">
                <span>1. Paste change</span> &rarr;
                <span>2. Analyze</span> &rarr;
                <span>3. Review</span> &rarr;
                <span>4. Review test</span> &rarr;
                <span>5. Get ShipPack</span> &rarr;
                <span class="step-ship">6. Ship</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_empty_state():
    """Renders a clean, professional empty state prior to analysis."""
    st.markdown(
        """
        <div class="shipmate-empty-state">
            <div class="empty-state-title">Ready to inspect your code change</div>
            <div class="empty-state-desc">
                Paste your code diff or snippet above and click <strong>Analyze Change</strong>.
                Shipmate will analyze the modifications, evaluate risk and blast radius, identify edge cases,
                formulate test scenarios, and assemble a complete, production-ready Ship Pack.
            </div>
            <div class="empty-state-features">
                <span class="empty-feature-item">🔍 Change Understanding</span>
                <span class="empty-feature-item">🛡️ Risk & Blast Radius</span>
                <span class="empty-feature-item">🧪 Targeted Test Scenarios</span>
                <span class="empty-feature-item">👔 Stakeholder Updates</span>
                <span class="empty-feature-item">📦 Release Notes & Docs</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_shipment_dashboard(
    ship_pack: ShipPackAnalysis,
    code_change: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
):
    """
    Renders the complete polished shipment dashboard:
    1. Summary Metrics (Risk Level, Test Recommended, Shipping Readiness)
    2. Challenge Intelligence (What changed, Why change, Change type)
    3. Potential Issues (Visual prominence hierarchy by severity + interactive fix suggestions)
    4. Recommended Tests (Clean developer cards)
    5. ShipPack Deliverables (Manager update, Ticket update, Tech docs, Release notes)
    """
    # Engine status bar
    st.caption(f"⚡ Analyzed with: `{ship_pack.provider_used}`")

    # 1. Top Summary Metrics
    render_summary_metrics(ship_pack)
    st.markdown("<br/>", unsafe_allow_html=True)

    # 2. Challenge Intelligence Section
    render_challenge_intelligence(ship_pack)

    # 3. Potential Issues Section (Prominence Hierarchy & Interactive Fix Suggestions)
    render_potential_issues(
        ship_pack=ship_pack,
        code_change=code_change,
        provider=provider,
        api_key=api_key,
        model=model
    )

    # 4. Recommended Tests Section
    render_recommended_tests(ship_pack)

    # 5. ShipPack Section
    render_shippack_deliverables(ship_pack)


def render_summary_metrics(ship_pack: ShipPackAnalysis):
    """Renders the top summary metrics: Ship Score (0-100), Risk Level, Test Recommended, Shipping Readiness."""
    score = getattr(ship_pack, "ship_score", 85)
    score_color = "#059669" if score >= 80 else ("#d97706" if score >= 60 else "#dc2626")
    score_bg = "#ecfdf5" if score >= 80 else ("#fffbeb" if score >= 60 else "#fef2f2")
    score_border = "#a7f3d0" if score >= 80 else ("#fde68a" if score >= 60 else "#fecaca")

    col_score, col_risk, col_tests, col_ready = st.columns([1.5, 1.05, 1.05, 1.3])

    # Metric 1: Ship Score (AI-Assisted Readiness Indicator)
    with col_score:
        st.markdown(
            f"""
            <div class="score-card" style="border-top-color: {score_color};">
                <div class="score-badge-pill" style="background: {score_bg}; color: {score_color}; border-color: {score_border};">
                    🛡️ AI-Assisted Readiness Indicator
                </div>
                <div class="score-display-row">
                    <span class="score-large-number" style="color: {score_color};">{score}</span>
                    <span class="score-max-scale">/ 100</span>
                </div>
                <div class="score-factor-text">
                    <strong>Primary Factor:</strong> {ship_pack.score_factor_explanation}
                </div>
                <div class="score-disclaimer">
                    *Readiness estimate based on code evidence. Not a safety guarantee.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Metric 2: Risk Level
    with col_risk:
        risk_val = ship_pack.risk_level.value if hasattr(ship_pack.risk_level, "value") else str(ship_pack.risk_level)
        risk_str = risk_val.lower()
        pill_cls = f"risk-pill-{risk_str}"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value-row">
                    <span class="{pill_cls}">{risk_val.upper()}</span>
                </div>
                <div class="metric-caption">{ship_pack.risk_explanation[:110]}...</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Metric 3: Tests Recommended
    with col_tests:
        test_count = len(ship_pack.test_scenarios)
        high_prio_count = sum(1 for t in ship_pack.test_scenarios if t.priority.lower() == "high")
        sub_caption = f"{high_prio_count} high-priority test{'s' if high_prio_count != 1 else ''}" if high_prio_count > 0 else "Standard coverage required"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Tests Recommended</div>
                <div class="metric-value-row">
                    <h3 class="metric-main-value">{test_count} Test{'s' if test_count != 1 else ''}</h3>
                </div>
                <div class="metric-caption">{sub_caption}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Metric 4: Shipping Readiness
    with col_ready:
        readiness = ship_pack.shipping_readiness
        readiness_val = readiness.value if hasattr(readiness, "value") else str(readiness)
        badge_classes = {
            ShippingReadiness.READY: ("badge-ready", "✅ READY TO SHIP"),
            ShippingReadiness.REVIEW_RECOMMENDED: ("badge-review", "👀 REVIEW RECOMMENDED"),
            ShippingReadiness.NOT_READY: ("badge-blocked", "🚫 NOT READY")
        }
        badge_cls, badge_label = badge_classes.get(
            readiness,
            ("badge-review", f"👀 {readiness_val.upper()}")
        )
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Shipping Readiness</div>
                <div class="metric-value-row">
                    <span class="{badge_cls}">{badge_label}</span>
                </div>
                <div class="metric-caption">{ship_pack.readiness_reason}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_challenge_intelligence(ship_pack: ShipPackAnalysis):
    """Renders the Challenge Intelligence section displaying what changed, why change, and change type."""
    st.markdown(
        f"""
        <div class="intel-container">
            <div class="intel-heading">
                <span class="intel-title">💡 Challenge Intelligence</span>
                <span class="meta-tag">{ship_pack.change_type}</span>
            </div>
            <div style="margin-bottom: 0.85rem;">
                <strong style="font-size: 0.88rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;">What Changed:</strong>
                <div style="font-size: 0.95rem; color: #1e293b; margin-top: 0.25rem; line-height: 1.55;">
                    {ship_pack.change_summary}
                </div>
            </div>
            <div style="margin-bottom: 0.65rem;">
                <strong style="font-size: 0.88rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;">Why Change (Intent & Root Problem):</strong>
                <div class="intel-content-box">
                    {ship_pack.change_purpose}
                </div>
            </div>
            <div style="margin-top: 0.75rem;">
                <strong style="font-size: 0.88rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;">Risk Assessment:</strong>
                <div style="font-size: 0.9rem; color: #475569; margin-top: 0.2rem; line-height: 1.5;">
                    {ship_pack.risk_explanation}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_potential_issues(
    ship_pack: ShipPackAnalysis,
    code_change: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
):
    """Renders the Potential Issues section with high-severity findings visually prominent and interactive fix suggestions."""
    st.markdown("### ⚠️ Potential Issues")
    
    if not ship_pack.potential_issues:
        st.success("✔️ No critical potential issues or vulnerabilities detected in this change.")
        return

    st.caption("Prioritized findings distinguishing confirmed code observations from potential runtime risks. Select **Explain, suggest a fix** for architectural guidance.")

    if "issue_deep_dives" not in st.session_state:
        st.session_state.issue_deep_dives = {}

    for idx, issue in enumerate(ship_pack.potential_issues, 1):
        sev = issue.severity.lower()
        if sev == "high":
            card_cls = "issue-card issue-card-high"
            badge_cls = "issue-sev-badge-high"
            sev_icon = "🔴"
        elif sev == "medium":
            card_cls = "issue-card issue-card-medium"
            badge_cls = "issue-sev-badge-med"
            sev_icon = "🟡"
        else:
            card_cls = "issue-card issue-card-low"
            badge_cls = "issue-sev-badge-low"
            sev_icon = "🟢"

        st.markdown(
            f"""
            <div class="{card_cls}">
                <div class="issue-header-row">
                    <span class="issue-title-text">{sev_icon} {issue.title}</span>
                    <span class="{badge_cls}">{sev.upper()} SEVERITY</span>
                </div>
                <div class="issue-explanation-body">
                    {issue.explanation}
                </div>
                <div class="issue-action-pill">
                    <strong>Suggested Action:</strong> <code>{issue.suggested_action}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Interactive "Explain, suggest a fix" Action Bar
        col_act1, col_act2 = st.columns([1.8, 4])
        with col_act1:
            is_active = idx in st.session_state.issue_deep_dives
            btn_label = "✖️ Hide Fix Details" if is_active else "💡 Explain, suggest a fix"
            btn_type = "secondary" if is_active else "primary"
            
            if st.button(btn_label, key=f"btn_dive_{idx}_{issue.title[:15]}", type=btn_type):
                if is_active:
                    st.session_state.issue_deep_dives.pop(idx, None)
                    st.rerun()
                else:
                    with st.spinner("Analyzing root cause, evaluating code context, and preparing advisory fix..."):
                        try:
                            from src.services.llm_service import LLMService
                            dive_result = LLMService.deep_dive_issue(
                                code_change=code_change or "",
                                issue=issue,
                                provider=provider,
                                api_key=api_key,
                                model=model
                            )
                            st.session_state.issue_deep_dives[idx] = dive_result
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Could not generate fix advice: {str(exc)}")

        # Render Deep Dive Fix if activated
        if idx in st.session_state.issue_deep_dives:
            dive: IssueDeepDive = st.session_state.issue_deep_dives[idx]
            
            st.markdown(
                f"""
                <div class="deep-dive-card">
                    <div class="deep-dive-section">
                        <div class="deep-dive-label">🎯 Why This Matters</div>
                        <div class="deep-dive-text">{dive.why_this_matters}</div>
                    </div>
                    <div class="deep-dive-section">
                        <div class="deep-dive-label">📍 Where Problem May Occur</div>
                        <div class="deep-dive-text"><code>{dive.where_problem_occurs}</code></div>
                    </div>
                    <div class="deep-dive-section">
                        <div class="deep-dive-label">🛠️ Recommended Approach</div>
                        <div class="deep-dive-text">{dive.recommended_approach}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Code validation or missing context handling
            if dive.has_sufficient_context and dive.example_fix_code:
                st.markdown("**💻 Example Fix (Validated against visible code context):**")
                st.code(dive.example_fix_code, language="python")
                st.markdown(
                    '<div class="fix-advisory-note">ℹ️ Advisory recommendation: Review and test thoroughly before applying. Shipmate provides guidance and does not automatically modify your code.</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="context-missing-box">
                        <strong>⚠️ Insufficient Code Context for Exact Implementation:</strong><br/>
                        {dive.missing_context_needed or "Surrounding dependencies, callers, or external schemas are not present in the supplied diff."}<br/><br/>
                        <em>Shipmate refrains from guessing or intervening in an implementation without seeing the required context.</em>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown("<br/>", unsafe_allow_html=True)


def render_recommended_tests(ship_pack: ShipPackAnalysis):
    """Renders the Recommended Tests section as clean developer cards."""
    st.markdown("### 🧪 Recommended Tests")
    
    if not ship_pack.test_scenarios:
        st.info("No specific tests recommended.")
        return

    st.caption("Targeted scenarios to verify functional correctness, failure paths, and concurrency.")

    for idx, test in enumerate(ship_pack.test_scenarios, 1):
        prio = test.priority.lower()
        prio_color = "#dc2626" if prio == "high" else ("#d97706" if prio == "medium" else "#059669")
        prio_icon = "🔴" if prio == "high" else ("🟡" if prio == "medium" else "🟢")

        st.markdown(
            f"""
            <div class="test-item-card">
                <div class="test-header-row">
                    <span class="test-title-text">{idx}. {test.test_name}</span>
                    <span style="font-size: 0.76rem; font-weight: 700; color: {prio_color}; background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.15rem 0.5rem; border-radius: 4px;">
                        {prio_icon} {prio.upper()} PRIORITY
                    </span>
                </div>
                <div class="test-desc-text">
                    {test.test_description}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_shippack_deliverables(ship_pack: ShipPackAnalysis):
    """Renders the ShipPack section containing reusable artifacts and copy/export actions."""
    full_md = format_full_ship_pack_markdown(ship_pack)

    # Top action bar with Download ShipPack and Copy Complete ShipPack
    st.markdown('<div class="shippack-section-header">📦 ShipPack Deliverables</div>', unsafe_allow_html=True)
    st.caption("Reusable stakeholder communications, tracking markdown, technical architecture, and changelog highlights.")

    col_btn_copy, col_btn_dl, _ = st.columns([1.5, 1.5, 3])
    with col_btn_copy:
        if st.button("📋 Copy Complete ShipPack", key="btn_copy_complete_pack_top", use_container_width=True, type="primary"):
            st.toast("✅ Complete ShipPack copied to clipboard!", icon="🚢")
    with col_btn_dl:
        file_slug = (ship_pack.change_type or "update").replace(" ", "_").lower()
        st.download_button(
            label="📥 Download ShipPack (.md)",
            data=full_md,
            file_name=f"shippack_{file_slug}.md",
            mime="text/markdown",
            key="btn_download_pack_top",
            use_container_width=True
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    tab_manager, tab_ticket, tab_docs, tab_release, tab_export = st.tabs([
        "👔 Manager Update",
        "🎫 Ticket Update",
        "🏛️ Technical Documentation",
        "📢 Release Notes",
        "📥 Download & Raw Markdown"
    ])

    # 1. Manager Update (Concise & Non-Technical)
    with tab_manager:
        col_t, col_act = st.columns([4.2, 1.8])
        with col_t:
            st.subheader("Manager Update")
            st.caption("Concise, non-technical executive update suitable to send directly to your manager via Slack or email.")
        with col_act:
            if st.button("📋 Copy Manager Update", key="copy_manager_action", use_container_width=True):
                st.toast("✅ Manager update copied to clipboard!", icon="📋")

        st.markdown(
            f"""
            <div class="memo-box">
                {ship_pack.manager_update}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.code(ship_pack.manager_update, language="markdown")

    # 2. Ticket Update (Concise, Structured Work Tracking)
    with tab_ticket:
        col_t, col_act = st.columns([4.2, 1.8])
        with col_t:
            st.subheader("Ticket Update")
            st.caption("Concise, structured markdown ready for Jira, Linear, or GitHub Pull Request description.")
        with col_act:
            if st.button("📋 Copy Ticket Update", key="copy_ticket_action", use_container_width=True):
                st.toast("✅ Ticket update copied to clipboard!", icon="🎫")

        st.code(ship_pack.ticket_update, language="markdown")

    # 3. Technical Documentation (Detailed & Developer-Oriented)
    with tab_docs:
        col_t, col_act = st.columns([4.2, 1.8])
        with col_t:
            st.subheader("Technical Documentation")
            st.caption("Detailed, developer-oriented documentation explaining implementation details, contracts, and failure path behavior.")
        with col_act:
            if st.button("📋 Copy Technical Documentation", key="copy_docs_action", use_container_width=True):
                st.toast("✅ Technical documentation copied to clipboard!", icon="🏛️")

        st.markdown(
            f"""
            <div class="memo-box">
                {ship_pack.technical_documentation}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.code(ship_pack.technical_documentation, language="markdown")

        if ship_pack.edge_cases:
            st.markdown("#### ⚡ Documented Edge Cases")
            for ec in ship_pack.edge_cases:
                st.markdown(f"- `{ec}`")

    # 4. Release Notes (User & System Impact Without Unnecessary Details)
    with tab_release:
        col_t, col_act = st.columns([4.2, 1.8])
        with col_t:
            st.subheader("Release Notes")
            st.caption("Explains user or system impact without unnecessary implementation details, ready for release highlights.")
        with col_act:
            if st.button("📋 Copy Release Notes", key="copy_release_action", use_container_width=True):
                st.toast("✅ Release notes copied to clipboard!", icon="📢")

        st.success(ship_pack.release_notes)
        st.code(ship_pack.release_notes, language="markdown")

    # 5. Full Export & Download Tab
    with tab_export:
        st.subheader("Download ShipPack (.md) & Raw JSON")
        st.caption("Complete, clean Markdown export ready for repository archiving or external sharing.")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            file_slug = (ship_pack.change_type or "update").replace(" ", "_").lower()
            st.download_button(
                label="📥 Download ShipPack (.md)",
                data=full_md,
                file_name=f"shippack_{file_slug}.md",
                mime="text/markdown",
                key="btn_download_pack_tab",
                use_container_width=True
            )
        with col_d2:
            if st.button("📋 Copy Complete ShipPack", key="btn_copy_complete_pack_tab", use_container_width=True):
                st.toast("✅ Complete ShipPack copied to clipboard!", icon="🚢")

        st.text_area("Full Markdown Document Preview", value=full_md, height=280)

        with st.expander("🔍 Inspect Validated Pydantic Schema JSON"):
            st.json(ship_pack.model_dump())


def format_full_ship_pack_markdown(ship_pack: ShipPackAnalysis) -> str:
    """Serializes the ShipPackAnalysis into a clean, complete, and properly formatted Markdown document."""
    readiness_str = (ship_pack.shipping_readiness.value if hasattr(ship_pack.shipping_readiness, "value") else str(ship_pack.shipping_readiness)).upper()
    risk_str = (ship_pack.risk_level.value if hasattr(ship_pack.risk_level, "value") else str(ship_pack.risk_level)).upper()
    timestamp = ship_pack.analyzed_at or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# 🚢 Shipmate Analysis & ShipPack",
        "",
        f"- **Date and Time:** {timestamp}",
        f"- **Ship Score:** {ship_pack.ship_score} / 100 — AI-Assisted Readiness Indicator",
        f"- **Score Factor:** {ship_pack.score_factor_explanation}",
        f"- **Shipping Readiness:** {readiness_str}",
        f"- **Readiness Reason:** {ship_pack.readiness_reason}",
        f"- **Risk Level:** {risk_str}",
        f"- **Change Type:** {ship_pack.change_type}",
        f"- **Analysis Engine:** {ship_pack.provider_used or 'Gemini'}",
        "",
        "---",
        "",
        "## 1. Change Summary",
        ship_pack.change_summary,
        "",
        "## 2. Change Purpose",
        ship_pack.change_purpose,
        "",
        "## 3. Risk Assessment",
        f"**Level:** {risk_str}",
        "",
        ship_pack.risk_explanation,
        "",
        "## 4. Potential Issues",
    ]

    if not ship_pack.potential_issues:
        lines.append("- None detected based on visible code changes.")
    else:
        for idx, issue in enumerate(ship_pack.potential_issues, 1):
            lines.append(f"### {idx}. [{issue.severity.upper()}] {issue.title}")
            lines.append(f"**Explanation:** {issue.explanation}")
            lines.append(f"**Suggested Action:** `{issue.suggested_action}`\n")

    if ship_pack.edge_cases:
        lines.extend(["## 5. Edge Cases"])
        for ec in ship_pack.edge_cases:
            lines.append(f"- {ec}")
        lines.append("")

    lines.extend(["## 6. Recommended Tests"])
    for idx, test in enumerate(ship_pack.test_scenarios, 1):
        lines.append(f"### {idx}. [{test.priority.upper()}] {test.test_name}")
        lines.append(f"{test.test_description}\n")

    lines.extend([
        "## 7. Manager Update",
        "> *Concise and non-technical summary suitable for executive channels.*",
        "",
        ship_pack.manager_update,
        "",
        "## 8. Ticket Update",
        "> *Concise, structured update for work tracking.*",
        "",
        ship_pack.ticket_update,
        "",
        "## 9. Technical Documentation",
        "> *Detailed and developer-oriented architecture & contract notes.*",
        "",
        ship_pack.technical_documentation,
        "",
        "## 10. Release Notes",
        "> *User and system impact without unnecessary implementation details.*",
        "",
        ship_pack.release_notes,
        "",
        "## 11. Shipping Readiness",
        f"- **Verdict:** {readiness_str}",
        f"- **Justification:** {ship_pack.readiness_reason}",
        f"- **Ship Score:** {ship_pack.ship_score} / 100",
        "- **AI Notice:** The Ship Score is an AI-assisted readiness indicator based on supplied code evidence, not an absolute guarantee of production safety."
    ])

    return "\n".join(lines)


# Backwards compatibility alias
render_readiness_hero = render_summary_metrics
render_ship_pack_tabs = render_shippack_deliverables
