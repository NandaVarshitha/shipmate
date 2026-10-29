"""
Shipmate FastAPI Backend for Vercel Serverless Deployment.
Exposes endpoints for code change analysis, deep dives, samples, and health checks.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Add project root to sys.path so 'src' imports resolve reliably in Vercel serverless environment
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.config import Config
from src.models import ShipPackAnalysis, PotentialIssue, IssueDeepDive
from src.sample_diffs import SAMPLE_DIFFS, DEMO_CHANGE
from src.services.llm_service import LLMService
from src.services.exceptions import (
    EmptyInputError,
    MissingAPIKeyError,
    RateLimitError,
    APIConnectionError,
    ModelResponseParseError
)

app = FastAPI(
    title="ShipMate API",
    description="AI-assisted code risk assessment and automated Ship Pack backend",
    version="0.1.0"
)

# Enable CORS for frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    code: str = Field(..., description="Git diff, patch, or source code to analyze")
    context: Optional[str] = Field(default="", description="Optional developer context or ticket info")
    input_type: Optional[str] = Field(default="Diff", description="Input type: Diff, Change, or Code")
    provider: Optional[str] = Field(default=None, description="gemini, openai, or demo")
    api_key: Optional[str] = Field(default=None, description="Optional API key override")
    model: Optional[str] = Field(default=None, description="Optional model name override")


class DeepDiveRequest(BaseModel):
    code: str
    issue: PotentialIssue
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


@app.get("/api/health")
def health():
    """Health check and environment configuration status."""
    return {
        "status": "healthy",
        "app": Config.APP_TITLE,
        "version": Config.APP_VERSION,
        "default_provider": Config.get_default_provider(),
        "has_gemini_key": bool(Config.get_gemini_api_key()),
        "has_openai_key": bool(Config.get_openai_api_key())
    }


@app.get("/api/samples")
def get_samples():
    """Returns curated demo change and preset sample diffs."""
    return {
        "demo_change": DEMO_CHANGE,
        "samples": SAMPLE_DIFFS
    }


@app.post("/api/analyze", response_model=ShipPackAnalysis)
def analyze_change(req: AnalyzeRequest):
    """Analyzes a code change and returns a structured ShipPackAnalysis."""
    if not req.code or not req.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code change cannot be empty. Please provide a git diff, patch, or source code."
        )

    context_str = f"[{req.input_type} Mode] {req.context}" if req.context else f"[{req.input_type} Mode]"

    try:
        analysis = LLMService.analyze(
            code_change=req.code,
            context=context_str,
            provider=req.provider,
            api_key=req.api_key,
            model=req.model
        )
        return analysis
    except EmptyInputError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except MissingAPIKeyError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{str(err)} Switch to 'Demo Mode' in the sidebar to test Shipmate without an API key, or configure GEMINI_API_KEY in Vercel Environment Variables."
        )
    except RateLimitError as err:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(err))
    except APIConnectionError as err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(err))
    except ModelResponseParseError as err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(err))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(exc)}")


@app.post("/api/deep-dive", response_model=IssueDeepDive)
def deep_dive(req: DeepDiveRequest):
    """Generates an architectural deep dive and advisory code fix for a potential issue."""
    try:
        result = LLMService.deep_dive_issue(
            code_change=req.code,
            issue=req.issue,
            provider=req.provider,
            api_key=req.api_key,
            model=req.model
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not generate fix advice: {str(exc)}"
        )


# Serve static frontend files when running locally
public_dir = ROOT_DIR / "public"
if public_dir.exists():
    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="static")
