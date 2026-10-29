"""
Shipmate: AI-Powered Developer Shipping Assistant
Streamlit Application Entrypoint
"""
from __future__ import annotations
import time
from datetime import datetime
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Shipmate — AI Developer Shipping Assistant",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Local imports
from src.config import Config
from src.sample_diffs import SAMPLE_DIFFS, DEMO_CHANGE
from src.services.llm_service import LLMService
from src.services.exceptions import (
    EmptyInputError,
    MissingAPIKeyError,
    RateLimitError,
    APIConnectionError,
    ModelResponseParseError
)
from src.ui.styles import CUSTOM_CSS
from src.ui.components import (
    render_header,
    render_empty_state,
    render_shipment_dashboard
)

# Inject modern developer tool styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initializes persistent session state variables."""
    if "input_type" not in st.session_state:
        st.session_state.input_type = "Diff"
    if "code_content" not in st.session_state:
        st.session_state.code_content = DEMO_CHANGE["diff"]
    if "content_context" not in st.session_state:
        st.session_state.content_context = DEMO_CHANGE["context"]
    if "current_ship_pack" not in st.session_state:
        st.session_state.current_ship_pack = None
    if "issue_deep_dives" not in st.session_state:
        st.session_state.issue_deep_dives = {}
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []


def main():
    init_session_state()

    # 1. Main Shipmate Interface Header
    render_header()

    # Sidebar: Provider Configuration, Fast Samples & Session History
    with st.sidebar:
        st.markdown("### ⚙️ Engine Settings")
        
        has_gemini = bool(Config.get_gemini_api_key())
        has_openai = bool(Config.get_openai_api_key())
        default_idx = 0 if has_gemini else (1 if has_openai else 2)

        provider_choice = st.selectbox(
            "AI Provider",
            options=["gemini", "openai", "demo"],
            format_func=lambda x: {
                "gemini": "Google Gemini (Recommended)",
                "openai": "OpenAI",
                "demo": "Demo Mode (Instant Offline)"
            }[x],
            index=default_idx
        )

        api_key_to_use = None
        model_name = ""

        if provider_choice == "gemini":
            user_gemini_input = st.text_input(
                "Gemini API Key",
                type="password",
                value="",
                placeholder="•••••••••••••••• (Loaded securely)" if has_gemini else "Paste Gemini API Key (or use Demo Mode)",
                help="Loaded securely from Streamlit secrets or enter manually to override"
            )
            if has_gemini:
                st.caption("🔒 Key loaded securely from Streamlit Secrets / Environment.")
            else:
                st.caption("💡 Enter a key above, or switch to **Demo Mode** to test without an API key.")

            api_key_to_use = user_gemini_input.strip() if user_gemini_input.strip() else Config.get_gemini_api_key()
            model_name = st.selectbox(
                "Model",
                options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
                index=0
            )
        elif provider_choice == "openai":
            user_openai_input = st.text_input(
                "OpenAI API Key",
                type="password",
                value="",
                placeholder="•••••••••••••••• (Loaded securely)" if has_openai else "Paste OpenAI API Key (or use Demo Mode)",
                help="Loaded securely from Streamlit secrets or enter manually to override"
            )
            if has_openai:
                st.caption("🔒 Key loaded securely from Streamlit Secrets / Environment.")
            else:
                st.caption("💡 Enter a key above, or switch to **Demo Mode** to test without an API key.")

            api_key_to_use = user_openai_input.strip() if user_openai_input.strip() else Config.get_openai_api_key()
            model_name = st.selectbox(
                "Model",
                options=["gpt-4o-mini", "gpt-4o"],
                index=0
            )
        else:
            st.info("💡 **Demo Mode Active**: Generates realistic Ship Packs locally without requiring API keys or network latency.")

        st.markdown("---")
        st.markdown("### ⚡ Quick-Load Presets")
        sample_key = st.selectbox(
            "Select Sample Code Change",
            options=list(SAMPLE_DIFFS.keys()),
            format_func=lambda k: SAMPLE_DIFFS[k]["title"]
        )

        if st.button("📥 Load Sample into Editor", use_container_width=True):
            st.session_state.code_content = SAMPLE_DIFFS[sample_key]["diff"]
            st.session_state.content_context = SAMPLE_DIFFS[sample_key]["context"]
            st.session_state.input_type = "Diff"
            st.session_state.current_ship_pack = None
            st.session_state.issue_deep_dives = {}
            st.rerun()

        st.caption(f"ℹ️ {SAMPLE_DIFFS[sample_key]['description']}")

        st.markdown("---")
        if st.button("🗑️ Clear Input", use_container_width=True):
            st.session_state.code_content = ""
            st.session_state.content_context = ""
            st.session_state.current_ship_pack = None
            st.session_state.issue_deep_dives = {}
            st.rerun()

        # Session Analysis History
        st.markdown("---")
        st.markdown("### 🕒 Session History")
        if not st.session_state.analysis_history:
            st.caption("No analyses performed in this session yet.")
        else:
            st.caption("Recent analyses in current session. Reopen to view artifacts:")
            for h_idx, entry in enumerate(st.session_state.analysis_history):
                short_ts = entry["timestamp"]
                with st.expander(f"📦 {short_ts} (Score: {entry['ship_score']})", expanded=(h_idx == 0)):
                    st.markdown(f"**Summary:** {entry['change_summary'][:95]}...")
                    st.markdown(f"**Risk:** `{entry['risk_level'].upper()}` &nbsp;|&nbsp; **Score:** `{entry['ship_score']}/100`")
                    st.markdown(f"**Readiness:** `{entry['shipping_readiness'].upper()}`")
                    if st.button("🔄 Reopen Result", key=f"reopen_{h_idx}_{entry['timestamp']}", use_container_width=True):
                        st.session_state.current_ship_pack = entry["pack"]
                        st.session_state.code_content = entry["code"]
                        st.session_state.content_context = entry["context"]
                        st.session_state.input_type = entry.get("input_type", "Diff")
                        st.session_state.issue_deep_dives = {}
                        st.toast("Reopened historical analysis!", icon="📦")
                        st.rerun()

    # 2. "Try Demo Change" Button & Input Type Selector
    col_demo, col_type = st.columns([1.6, 2.4])
    with col_demo:
        if st.button("⚡ Try Demo Change", type="secondary", use_container_width=True, help="Populate realistic payment webhook retry code with potential concurrency and blocking risks"):
            st.session_state.code_content = DEMO_CHANGE["diff"]
            st.session_state.content_context = DEMO_CHANGE["context"]
            st.session_state.input_type = "Diff"
            st.session_state.current_ship_pack = None
            st.session_state.issue_deep_dives = {}
            st.toast("Loaded Demo Change (External API with 3-Attempt Retry)!", icon="⚡")
            st.rerun()

    with col_type:
        input_type = st.radio(
            "Input Type",
            options=["Diff", "Change", "Code"],
            horizontal=True,
            index=["Diff", "Change", "Code"].index(st.session_state.input_type)
        )
        st.session_state.input_type = input_type

    st.caption("💡 Select **Try Demo Change** to test Shipmate on an external API retry handler with concurrency & thread starvation risks.")

    # Dynamic placeholder based on input type
    placeholders = {
        "Diff": "diff --git a/services/auth.py b/services/auth.py\n--- a/services/auth.py\n+++ b/services/auth.py\n@@ -20,6 +20,11 @@\n...",
        "Change": "Paste description or before/after modifications across files...",
        "Code": "Paste modified function, class, or full file contents..."
    }

    # Large code input area titled "Your Code Change"
    code_text = st.text_area(
        label="Your Code Change",
        value=st.session_state.code_content,
        height=280,
        placeholder=placeholders.get(input_type, "Paste your code change here..."),
        help="Paste a git diff, summary of changes, or raw source code."
    )

    # Optional text field called "Content" below the input
    content_text = st.text_input(
        label="Content",
        value=st.session_state.content_context,
        placeholder="Explain the feature or ticket (e.g. JIRA-102: Fix auth token refresh race condition)",
        help="Optional context regarding the ticket, feature requirement, or intent."
    )

    # 3. Prominent Action Button: "Analyze Change"
    analyze_clicked = st.button(
        "Analyze Change",
        type="primary",
        use_container_width=True
    )

    if analyze_clicked:
        try:
            with st.status("Analyzing code change with Shipmate...", expanded=True) as status_box:
                status_box.write("🔍 Understanding code change...")
                time.sleep(0.12)
                status_box.write("🧠 Analyzing affected behavior...")
                time.sleep(0.12)
                status_box.write("🛡️ Looking for potential risks & edge cases...")

                ship_pack = LLMService.analyze(
                    code_change=code_text,
                    context=f"[{input_type} Mode] {content_text}" if content_text else f"[{input_type} Mode]",
                    provider=provider_choice,
                    api_key=api_key_to_use,
                    model=model_name
                )

                status_box.write("🧪 Generating test scenarios...")
                time.sleep(0.12)
                status_box.write("📦 Preparing your ShipPack...")
                status_box.update(label="✅ Analysis complete — ShipPack ready!", state="complete", expanded=False)

            # Update session state and history
            st.session_state.current_ship_pack = ship_pack
            st.session_state.issue_deep_dives = {}

            history_entry = {
                "timestamp": ship_pack.analyzed_at or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "change_summary": ship_pack.change_summary,
                "risk_level": ship_pack.risk_level.value if hasattr(ship_pack.risk_level, "value") else str(ship_pack.risk_level),
                "ship_score": getattr(ship_pack, "ship_score", 85),
                "shipping_readiness": ship_pack.shipping_readiness.value if hasattr(ship_pack.shipping_readiness, "value") else str(ship_pack.shipping_readiness),
                "pack": ship_pack,
                "code": code_text,
                "context": content_text,
                "input_type": input_type
            }
            # Maintain last 10 entries in session state
            st.session_state.analysis_history.insert(0, history_entry)
            st.session_state.analysis_history = st.session_state.analysis_history[:10]

            st.toast("Ship Pack ready!", icon="🚢")
        except EmptyInputError as err:
            st.warning(f"⚠️ {str(err)}")
        except MissingAPIKeyError as err:
            st.error(f"🔑 Missing API Key: {str(err)}")
            st.info("💡 Tip: You can switch to **Demo Mode** in the sidebar to test Shipmate without an API key, or add `GEMINI_API_KEY` to your Streamlit Community Cloud Secrets.")
        except RateLimitError as err:
            st.error(f"⏳ Rate Limit Exceeded: {str(err)}")
        except APIConnectionError as err:
            st.error(f"🌐 API Error: {str(err)}")
        except ModelResponseParseError as err:
            st.error(f"⚠️ Invalid Model Response: {str(err)}")
        except Exception as exc:
            st.error(f"❌ Unexpected error during analysis: {str(exc)}")

    # 4. Results or Clean Empty State
    if st.session_state.current_ship_pack:
        st.markdown("---")
        render_shipment_dashboard(
            ship_pack=st.session_state.current_ship_pack,
            code_change=code_text,
            provider=provider_choice,
            api_key=api_key_to_use,
            model=model_name
        )
    else:
        # Pre-analysis clean empty state
        render_empty_state()


if __name__ == "__main__":
    main()
