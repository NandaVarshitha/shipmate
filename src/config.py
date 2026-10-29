"""
Configuration manager for Shipmate.
Supports Streamlit Community Cloud secrets (st.secrets) with fallback
to environment variables (.env) for local development.
"""
from __future__ import annotations
import os
from typing import Optional
from dotenv import load_dotenv

# Load .env if present in project root (for local development)
load_dotenv()


def get_secret_or_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely retrieves a configuration key.
    Order of precedence:
    1. Streamlit secrets (st.secrets[KEY]) for Streamlit Community Cloud
    2. OS Environment variables (os.getenv(KEY)) from .env for local development
    3. Provided default value
    """
    # 1. Check Streamlit Secrets (Community Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if key in st.secrets:
                val = st.secrets[key]
                if val is not None and str(val).strip():
                    return str(val).strip()
            # Also check lowercase
            lower_k = key.lower()
            if lower_k in st.secrets:
                val = st.secrets[lower_k]
                if val is not None and str(val).strip():
                    return str(val).strip()
    except Exception:
        pass

    # 2. Check Environment Variables (.env)
    env_val = os.getenv(key)
    if env_val and env_val.strip():
        return env_val.strip()

    env_lower = os.getenv(key.lower())
    if env_lower and env_lower.strip():
        return env_lower.strip()

    return default


class ConfigMeta(type):
    """Metaclass allowing dynamic property access on Config (e.g. Config.GEMINI_API_KEY)."""

    @property
    def GEMINI_API_KEY(cls) -> Optional[str]:
        return cls.get_gemini_api_key()

    @property
    def GEMINI_MODEL(cls) -> str:
        return cls.get_gemini_model()

    @property
    def OPENAI_API_KEY(cls) -> Optional[str]:
        return cls.get_openai_api_key()

    @property
    def OPENAI_MODEL(cls) -> str:
        return cls.get_openai_model()

    @property
    def DEFAULT_PROVIDER(cls) -> str:
        return cls.get_default_provider()


class Config(metaclass=ConfigMeta):
    """Application settings and API credentials."""

    @classmethod
    def get_gemini_api_key(cls) -> Optional[str]:
        return get_secret_or_env("GEMINI_API_KEY")

    @classmethod
    def get_gemini_model(cls) -> str:
        return get_secret_or_env("GEMINI_MODEL", "gemini-1.5-flash")

    @classmethod
    def get_openai_api_key(cls) -> Optional[str]:
        return get_secret_or_env("OPENAI_API_KEY")

    @classmethod
    def get_openai_model(cls) -> str:
        return get_secret_or_env("OPENAI_MODEL", "gpt-4o-mini")

    @classmethod
    def get_default_provider(cls) -> str:
        prov = (get_secret_or_env("DEFAULT_PROVIDER", "gemini") or "gemini").lower()
        return prov if prov in ("gemini", "openai", "demo") else "gemini"

    # App Settings
    APP_TITLE: str = "Shipmate"
    APP_TAGLINE: str = "AI-Powered Developer Shipping Assistant"
    APP_VERSION: str = "0.1.0"
