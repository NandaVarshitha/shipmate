"""
Analyzer Service Facade.
Provides a unified entrypoint forwarding to LLMService.
"""
from __future__ import annotations
from typing import Optional
from src.models import ShipPackAnalysis
from src.services.llm_service import LLMService


class AnalyzerService:
    """Facade for code change analysis."""

    @classmethod
    def analyze_diff(
        cls,
        diff_text: str,
        context: Optional[str] = None,
        provider_name: str = "gemini",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> ShipPackAnalysis:
        """Analyzes a code change or git diff."""
        return LLMService.analyze(
            code_change=diff_text,
            context=context,
            provider=provider_name,
            api_key=api_key,
            model=model_name
        )
