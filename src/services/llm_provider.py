"""
LLM Provider implementations supporting Gemini, OpenAI, and high-fidelity Demo Mode.
"""
from __future__ import annotations
import json
import logging
import re
from typing import Optional, Dict, Any
import requests

from src.prompts import SYSTEM_PROMPT, build_analysis_prompt

logger = logging.getLogger(__name__)


class LLMProvider:
    """Base interface for AI analysis providers."""
    
    def generate_ship_pack_json(self, diff: str, context: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    """Google Gemini API provider using direct HTTP REST."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )

    def generate_ship_pack_json(self, diff: str, context: Optional[str] = None) -> Dict[str, Any]:
        prompt = build_analysis_prompt(diff, context)
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        response = requests.post(
            self.endpoint,
            params=params,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            error_msg = f"Gemini API error ({response.status_code}): {response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        data = response.json()
        try:
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return clean_and_parse_json(raw_text)
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected response structure from Gemini: {data}") from exc


class OpenAIProvider(LLMProvider):
    """OpenAI API provider using direct HTTP REST."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def generate_ship_pack_json(self, diff: str, context: Optional[str] = None) -> Dict[str, Any]:
        prompt = build_analysis_prompt(diff, context)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            error_msg = f"OpenAI API error ({response.status_code}): {response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        data = response.json()
        raw_text = data["choices"][0]["message"]["content"]
        return clean_and_parse_json(raw_text)


class DemoMockProvider(LLMProvider):
    """High-fidelity offline generator for hackathon presentations and instant tests."""

    def generate_ship_pack_json(self, diff: str, context: Optional[str] = None) -> Dict[str, Any]:
        # Context-aware mock selection
        if "lock" in diff.lower() or "token" in diff.lower() or "auth" in diff.lower():
            return {
                "summary": {
                    "headline": "Auth Token Expiry Double-Checked Locking & Refresh Hardening",
                    "what_changed": [
                        "Introduced threading.Lock to synchronize concurrent access token refresh calls",
                        "Implemented 30-second pre-expiration refresh window to avoid in-flight 401s",
                        "Added network timeout (5.0s) and proper exception wrapping with AuthRefreshError",
                        "Handled refresh token rotation when returned by the OAuth server"
                    ],
                    "why_changed": "Under concurrent request surges, multiple threads noticed an expired access token simultaneously, creating a thundering-herd refresh storm that triggered OAuth rate limits and invalid token revocations.",
                    "impacted_components": ["services/auth_client.py", "OAuth Session Manager", "Downstream API Clients"]
                },
                "risk": {
                    "level": "MEDIUM",
                    "score": 45,
                    "rationale": "Touches core authentication flow. Thread locking prevents races, but lock contention could cause latency spikes if token endpoint hangs. 5-second timeout mitigates this.",
                    "blast_radius": "All authenticated outbound HTTP calls made by background workers or worker threads.",
                    "breaking_changes": False
                },
                "bugs_and_edge_cases": [
                    {
                        "title": "OAuth Server Outage Cascading Failure",
                        "severity": "HIGH",
                        "scenario": "If the internal OAuth server fails or exceeds 5s timeout, all threads queueing on _lock will fail consecutively.",
                        "mitigation": "Add a short circuit circuit-breaker or backoff before retrying refresh."
                    },
                    {
                        "title": "Clock Skew on Host Machine",
                        "severity": "LOW",
                        "scenario": "Host machine system time drifting backwards can calculate incorrect expires_at values.",
                        "mitigation": "Use time.monotonic() for elapsed duration calculations instead of time.time()."
                    }
                ],
                "test_scenarios": [
                    {
                        "category": "Unit Test",
                        "title": "Concurrent Access Simulation",
                        "steps": [
                            "Spawn 20 parallel worker threads attempting get_valid_token() simultaneously with an expired token",
                            "Mock OAuth network endpoint to verify exactly 1 POST request is executed"
                        ],
                        "expected_result": "All 20 threads receive valid token, OAuth endpoint called only once."
                    },
                    {
                        "category": "Manual QA",
                        "title": "Refresh Token Rotation Verification",
                        "steps": [
                            "Trigger token refresh where OAuth response supplies a new refresh_token",
                            "Inspect session state to confirm self.refresh_token is updated"
                        ],
                        "expected_result": "Subsequent calls use the newly rotated refresh token."
                    },
                    {
                        "category": "Edge Case / Chaos",
                        "title": "OAuth Timeout & Recovery",
                        "steps": [
                            "Simulate 6-second latency on OAuth endpoint",
                            "Ensure AuthRefreshError is raised within 5.0 seconds and lock is released"
                        ],
                        "expected_result": "Lock is freed and thread does not hang indefinitely."
                    }
                ],
                "manager_update": {
                    "headline": "Resolved intermittent 401 logout issues during high traffic",
                    "executive_summary": "We fixed a race condition in our internal authentication layer that occasionally caused users and background tasks to experience random session expirations. The fix synchronizes token refreshes safely.",
                    "business_impact": "Eliminates failed background synchronization jobs and prevents unnecessary user re-logins during peak hours.",
                    "deployment_risk_assessment": "Low risk, can be deployed with standard rolling deployment. No database migrations required."
                },
                "ticket_update": {
                    "pr_title_suggestion": "fix(auth): prevent concurrent token refresh storms with double-checked lock",
                    "markdown_content": "### Description\nFixes intermittent 401s caused by simultaneous token refresh triggers when access token expires.\n\n### Changes\n- Add `threading.Lock` with double-checked locking\n- Add 30s buffer before expiration\n- Add 5s timeout on OAuth HTTP requests\n- Rotate refresh token when provided by server\n\n### Checklist\n- [x] Unit tests for concurrent token access\n- [x] Tested with mocked OAuth timeout\n- [x] Zero breaking API changes",
                    "checklist": [
                        "Verify unit tests pass locally with 50 concurrent threads",
                        "Verify OAuth timeout logs AuthRefreshError cleanly",
                        "Ensure no circular imports with threading module"
                    ]
                },
                "technical_docs": {
                    "architecture_notes": "The `AuthenticatedSession` class now employs double-checked thread synchronization. Token refresh is guaranteed to be single-flighted per process.",
                    "api_or_contract_changes": "None. The public interface of `get_valid_token()` remains identical.",
                    "maintenance_notes": "Note that `_lock` is in-process only. If scaling to multi-process (e.g. Celery prefork or multiple uWSGI workers), token caching across processes still relies on centralized Redis if required."
                },
                "release_notes": {
                    "customer_facing": "Improved stability and background synchronization reliability under heavy application usage.",
                    "internal_changelog": "auth_client: added double-checked lock and timeout handling for token refresh"
                },
                "readiness": {
                    "verdict": "READY_TO_SHIP",
                    "readiness_score": 92,
                    "verdict_summary": "Clean, defensive implementation of a well-understood concurrency pattern. Thoroughly handles timeouts and rotation.",
                    "actionable_blockers": [
                        "Run test suite with `pytest -k test_auth_client`",
                        "Verify staging OAuth endpoint URL matches production credentials"
                    ]
                }
            }
        elif "webhook" in diff.lower() or "stripe" in diff.lower():
            return {
                "summary": {
                    "headline": "Stripe Webhook Idempotency & Database Transaction Wrapping",
                    "what_changed": [
                        "Wrapped webhook event processing in atomic database transaction (`session.begin()`)",
                        "Persisted processed event IDs in `WebhookEvent` table to reject duplicate events",
                        "Added early return for already-processed payment intents"
                    ],
                    "why_changed": "Network retries from Stripe were occasionally crediting users twice when initial webhook responses were delayed.",
                    "impacted_components": ["billing/webhooks.py", "Database `WebhookEvent` and `UserCredit` tables"]
                },
                "risk": {
                    "level": "HIGH",
                    "score": 75,
                    "rationale": "Directly affects financial transactions and billing balance. High risk of race condition if two identical webhook deliveries arrive in parallel before first commits.",
                    "blast_radius": "User billing balances, subscription activation, and revenue reporting.",
                    "breaking_changes": False
                },
                "bugs_and_edge_cases": [
                    {
                        "title": "Concurrent Delivery Race Condition",
                        "severity": "HIGH",
                        "scenario": "If Stripe sends 2 identical webhook requests within milliseconds, both may pass the `existing` check before either commits the `WebhookEvent` record.",
                        "mitigation": "Ensure `WebhookEvent.id` has a unique database constraint so the second transaction fails with an integrity error."
                    }
                ],
                "test_scenarios": [
                    {
                        "category": "Integration Test",
                        "title": "Idempotency Replay Test",
                        "steps": [
                            "Post the same valid payment_intent.succeeded payload twice",
                            "Verify user credit is only increased once and second call returns status: already_processed"
                        ],
                        "expected_result": "No duplicate credit applied."
                    }
                ],
                "manager_update": {
                    "headline": "Fixed double-crediting vulnerability in payment processing",
                    "executive_summary": "Added safeguard to guarantee customers are only credited once per transaction, even if payment provider resends webhook notifications.",
                    "business_impact": "Prevents revenue leakage and accounting discrepancies.",
                    "deployment_risk_assessment": "Medium-High. Monitor billing error logs closely for 30 minutes after deployment."
                },
                "ticket_update": {
                    "pr_title_suggestion": "fix(billing): enforce idempotency and transaction boundaries on Stripe webhooks",
                    "markdown_content": "### Summary\nGuarantees idempotency for payment webhooks by persisting event IDs inside an atomic transaction.\n\n### Verification\n- Tested with simulated duplicate Stripe events\n- DB transactions roll back on failure",
                    "checklist": [
                        "Confirm `WebhookEvent.id` has primary key / unique index in DB migration",
                        "Verify Stripe signature secret is configured in environment"
                    ]
                },
                "technical_docs": {
                    "architecture_notes": "All payment webhooks now use transaction-level idempotency checking against the `WebhookEvent` ledger.",
                    "api_or_contract_changes": "Returns `{'status': 'already_processed'}` with HTTP 200 on duplicate events.",
                    "maintenance_notes": "Ensure periodic pruning or partitioning of `WebhookEvent` table if volume exceeds 10M rows/month."
                },
                "release_notes": {
                    "customer_facing": "Enhanced payment processing security and reliability.",
                    "internal_changelog": "billing: wrap payment_intent webhook processing in atomic idempotency transaction"
                },
                "readiness": {
                    "verdict": "NEEDS_TESTING",
                    "readiness_score": 78,
                    "verdict_summary": "Code logic is solid, but needs verification that the DB schema has a unique constraint on WebhookEvent.id to prevent concurrent insert races.",
                    "actionable_blockers": [
                        "Verify DB schema migration has UNIQUE constraint on WebhookEvent(id)",
                        "Run concurrent webhook replay test"
                    ]
                }
            }
        else:
            # Generic fallback mock
            return {
                "summary": {
                    "headline": "Configuration & Infrastructure Resilience Refactor",
                    "what_changed": [
                        "Replaced hardcoded configuration values with environment variables",
                        "Added connection pooling, health pre-ping checks, and pool recycle timeouts",
                        "Configured graceful reconnect handling on stale socket drops"
                    ],
                    "why_changed": "Prevent production crashes and 500 errors caused by database connection drops after idle timeouts.",
                    "impacted_components": ["core/database.py", "Infrastructure / ORM Layer"]
                },
                "risk": {
                    "level": "LOW",
                    "score": 25,
                    "rationale": "Non-breaking configuration change. Improves stability without altering queries or business logic.",
                    "blast_radius": "Database connection lifecycle for all web requests.",
                    "breaking_changes": False
                },
                "bugs_and_edge_cases": [
                    {
                        "title": "Missing Environment Variable Fallback",
                        "severity": "LOW",
                        "scenario": "If DATABASE_URL is misconfigured or empty in staging, connection will fail immediately at startup.",
                        "mitigation": "Validate DATABASE_URL syntax on application boot."
                    }
                ],
                "test_scenarios": [
                    {
                        "category": "Manual QA",
                        "title": "Idle Connection Recovery",
                        "steps": [
                            "Leave application idle for 35 minutes (past pool_recycle limit)",
                            "Issue a new API request that executes a database query"
                        ],
                        "expected_result": "Pre-ping detects stale connection and automatically reconnects without user-facing 500."
                    }
                ],
                "manager_update": {
                    "headline": "Database connection stability improvement completed",
                    "executive_summary": "Improved database connection management to eliminate random connection drops during quiet traffic periods.",
                    "business_impact": "Improves overall API uptime and eliminates intermittent 500 errors.",
                    "deployment_risk_assessment": "Very safe. Rolling restart can be performed with zero downtime."
                },
                "ticket_update": {
                    "pr_title_suggestion": "refactor(db): add connection pooling, pre-ping check, and pool recycling",
                    "markdown_content": "### Summary\nConfigures connection pooling parameters on the primary SQLAlchemy engine to prevent stale connections.\n\n### Changes\n- pool_recycle=1800\n- pool_pre_ping=True\n- pool_size=20, max_overflow=10",
                    "checklist": [
                        "Confirmed DATABASE_URL is set in all deployment targets",
                        "Local unit tests pass"
                    ]
                },
                "technical_docs": {
                    "architecture_notes": "Connection pooling now actively probes the socket before checkout with pool_pre_ping.",
                    "api_or_contract_changes": "None.",
                    "maintenance_notes": "Monitor total open DB connections in RDS/CloudSQL metrics after deploy."
                },
                "release_notes": {
                    "customer_facing": "Performance and reliability improvements across backend services.",
                    "internal_changelog": "database: configure engine pool_pre_ping and pool_recycle"
                },
                "readiness": {
                    "verdict": "READY_TO_SHIP",
                    "readiness_score": 96,
                    "verdict_summary": "Low risk, high impact resilience fix. Ready for deployment.",
                    "actionable_blockers": []
                }
            }


def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """Cleans up markdown code fences and parses JSON securely."""
    text = raw_text.strip()
    
    # Strip ```json ... ``` wrapper if present
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        # Fallback regex search for { ... }
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not parse valid JSON from LLM response:\n{raw_text[:400]}...") from exc
