"""
AI Analysis Layer: Separate service for interacting with LLM providers
and producing strictly validated Pydantic structured output.
"""
from __future__ import annotations
import json
import logging
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import requests
from pydantic import ValidationError

from src.config import Config
from src.models import (
    ShipPackAnalysis,
    RiskLevel,
    ShippingReadiness,
    PotentialIssue,
    TestScenario,
    IssueDeepDive
)
from src.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_issue_deep_dive_prompt
)
from src.services.exceptions import (
    EmptyInputError,
    MissingAPIKeyError,
    RateLimitError,
    APIConnectionError,
    ModelResponseParseError
)

logger = logging.getLogger(__name__)


class LLMService:
    """
    Dedicated service for analyzing code changes with LLMs (Gemini, OpenAI, or Mock).
    Reads credentials strictly from environment variables without hardcoding.
    """

    @classmethod
    def analyze(
        cls,
        code_change: str,
        context: Optional[str] = None,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> ShipPackAnalysis:
        """
        Submits code change and optional context to the LLM and validates
        the structured output against the ShipPackAnalysis Pydantic model.
        """
        # 1. Guard against empty input
        if not code_change or not code_change.strip():
            raise EmptyInputError("Code change cannot be empty. Please provide a git diff, patch, or source code.")

        clean_code = code_change.strip()
        selected_provider = (provider or Config.DEFAULT_PROVIDER or "gemini").lower()

        # 2. Route to provider
        if selected_provider == "gemini":
            key = api_key or Config.get_gemini_api_key() or os.getenv("GEMINI_API_KEY")
            if not key or key.strip() in ("your_gemini_api_key_here", ""):
                raise MissingAPIKeyError(
                    "Gemini API key is not configured. Please add GEMINI_API_KEY to your Streamlit secrets or enter it in the sidebar."
                )
            target_model = model or Config.get_gemini_model() or "gemini-1.5-flash"
            raw_data = cls._call_gemini(clean_code, context, key.strip(), target_model)
            provider_label = f"Google Gemini ({target_model})"

        elif selected_provider == "openai":
            key = api_key or Config.get_openai_api_key() or os.getenv("OPENAI_API_KEY")
            if not key or key.strip() in ("your_openai_api_key_here", ""):
                raise MissingAPIKeyError(
                    "OpenAI API key is not configured. Please add OPENAI_API_KEY to your Streamlit secrets or enter it in the sidebar."
                )
            target_model = model or Config.get_openai_model() or "gpt-4o-mini"
            raw_data = cls._call_openai(clean_code, context, key.strip(), target_model)
            provider_label = f"OpenAI ({target_model})"

        elif selected_provider == "demo":
            raw_data = cls._generate_mock_analysis(clean_code, context)
            provider_label = "Demo Simulation Mode"

        else:
            raise ValueError(f"Unsupported provider '{selected_provider}'. Supported options: 'gemini', 'openai', 'demo'.")

        # 3. Validate structured output through Pydantic proxy model
        try:
            analysis = ShipPackAnalysis.model_validate(raw_data)
            analysis.provider_used = provider_label
            if not analysis.analyzed_at:
                analysis.analyzed_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            return analysis
        except ValidationError as val_err:
            logger.error("Pydantic validation failed for LLM response: %s", val_err)
            raise ModelResponseParseError(
                f"Model returned data that did not conform to the required Ship Pack schema: {val_err}"
            ) from val_err

    @classmethod
    def deep_dive_issue(
        cls,
        code_change: str,
        issue: PotentialIssue,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> IssueDeepDive:
        """
        Interactive action: Explains why a specific issue matters, where it may occur,
        recommends an approach, and suggests an example fix if enough code context exists.
        """
        if not code_change or not code_change.strip():
            raise EmptyInputError("Code change cannot be empty.")

        clean_code = code_change.strip()
        selected_provider = (provider or Config.DEFAULT_PROVIDER or "gemini").lower()
        prompt = build_issue_deep_dive_prompt(
            clean_code,
            issue.title,
            issue.explanation,
            issue.suggested_action
        )

        if selected_provider == "gemini":
            key = api_key or Config.get_gemini_api_key() or os.getenv("GEMINI_API_KEY")
            if not key or key.strip() in ("your_gemini_api_key_here", ""):
                raw_data = cls._generate_mock_deep_dive(clean_code, issue)
            else:
                target_model = model or Config.get_gemini_model() or "gemini-1.5-flash"
                raw_data = cls._call_gemini_raw(prompt, key.strip(), target_model)

        elif selected_provider == "openai":
            key = api_key or Config.get_openai_api_key() or os.getenv("OPENAI_API_KEY")
            if not key or key.strip() in ("your_openai_api_key_here", ""):
                raw_data = cls._generate_mock_deep_dive(clean_code, issue)
            else:
                target_model = model or Config.get_openai_model() or "gpt-4o-mini"
                raw_data = cls._call_openai_raw(prompt, key.strip(), target_model)

        else:
            raw_data = cls._generate_mock_deep_dive(clean_code, issue)

        try:
            return IssueDeepDive.model_validate(raw_data)
        except ValidationError as val_err:
            logger.error("Pydantic validation failed for IssueDeepDive: %s", val_err)
            raise ModelResponseParseError(f"Model returned invalid schema for fix suggestion: {val_err}") from val_err

    @classmethod
    def _sanitize_err(cls, msg: Any, key: Optional[str] = None) -> str:
        """Strips out sensitive API keys from error messages before presenting or logging."""
        cleaned = str(msg)
        if key and key.strip():
            cleaned = cleaned.replace(key.strip(), "[REDACTED_API_KEY]")
        cleaned = re.sub(r'([?&]key=)[^& \'"\)]+', r'\1[REDACTED_KEY]', cleaned)
        return cleaned

    @classmethod
    def _call_gemini(
        cls,
        code_change: str,
        context: Optional[str],
        api_key: str,
        model: str
    ) -> Dict[str, Any]:
        """Calls Google Gemini REST API using structured JSON output mode."""
        prompt = build_analysis_prompt(code_change, context)
        return cls._call_gemini_raw(prompt, api_key, model)

    @classmethod
    def _call_gemini_raw(cls, prompt: str, api_key: str, model: str) -> Dict[str, Any]:
        """Sends arbitrary structured JSON prompt to Gemini."""
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        params = {"key": api_key}
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
                "temperature": 0.1
            }
        }

        try:
            response = requests.post(
                endpoint,
                params=params,
                headers=headers,
                json=payload,
                timeout=60
            )
        except requests.exceptions.Timeout as timeout_err:
            raise APIConnectionError("Gemini API request timed out after 60 seconds. Please check your network and try again.") from timeout_err
        except requests.exceptions.RequestException as req_err:
            sanitized = cls._sanitize_err(req_err, api_key)
            raise APIConnectionError(f"Failed to connect to Gemini API: {sanitized}") from req_err

        if response.status_code == 429:
            raise RateLimitError("Gemini API rate limit exceeded (HTTP 429). Please wait a few seconds before retrying.")

        if response.status_code != 200:
            try:
                err_json = response.json()
                msg = err_json.get("error", {}).get("message", response.text)
            except Exception:
                msg = response.text
            sanitized_msg = cls._sanitize_err(msg, api_key)
            raise APIConnectionError(f"Gemini API returned HTTP {response.status_code}: {sanitized_msg}")

        try:
            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return cls._clean_and_parse_json(raw_text)
        except (KeyError, IndexError, ValueError) as exc:
            raise ModelResponseParseError(f"Failed to extract JSON from Gemini candidate response: {str(exc)}") from exc

    @classmethod
    def _call_openai(
        cls,
        code_change: str,
        context: Optional[str],
        api_key: str,
        model: str
    ) -> Dict[str, Any]:
        """Calls OpenAI Chat Completions API with JSON object response format."""
        prompt = build_analysis_prompt(code_change, context)
        return cls._call_openai_raw(prompt, api_key, model)

    @classmethod
    def _call_openai_raw(cls, prompt: str, api_key: str, model: str) -> Dict[str, Any]:
        """Sends arbitrary structured JSON prompt to OpenAI."""
        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        except requests.exceptions.Timeout as timeout_err:
            raise APIConnectionError("OpenAI API request timed out after 60 seconds. Please check your network and try again.") from timeout_err
        except requests.exceptions.RequestException as req_err:
            sanitized = cls._sanitize_err(req_err, api_key)
            raise APIConnectionError(f"Failed to connect to OpenAI API: {sanitized}") from req_err

        if response.status_code == 429:
            raise RateLimitError("OpenAI API rate limit exceeded (HTTP 429). Please wait a few moments before retrying.")

        if response.status_code != 200:
            try:
                err_json = response.json()
                msg = err_json.get("error", {}).get("message", response.text)
            except Exception:
                msg = response.text
            sanitized_msg = cls._sanitize_err(msg, api_key)
            raise APIConnectionError(f"OpenAI API returned HTTP {response.status_code}: {sanitized_msg}")

        try:
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]
            return cls._clean_and_parse_json(raw_text)
        except (KeyError, IndexError, ValueError) as exc:
            raise ModelResponseParseError(f"Failed to extract JSON from OpenAI response: {str(exc)}") from exc

    @classmethod
    def _generate_mock_deep_dive(cls, code_change: str, issue: PotentialIssue) -> Dict[str, Any]:
        """Grounded mock deep dive with concrete fix or explicit missing context."""
        title_lower = issue.title.lower()

        if "process boundary" in title_lower or "in-memory" in title_lower:
            return {
                "why_this_matters": "Python's `threading.Lock` is strictly local to a single operating system process memory space. If the application is served using multiple worker processes (such as Gunicorn with prefork workers, uWSGI, or multiple container replicas), each process will maintain its own independent lock and token expiration state, resulting in duplicate token refresh storms across processes.",
                "where_problem_occurs": "services/auth_client.py: in __init__ at 'self._lock = threading.Lock()'.",
                "recommended_approach": "Replace the in-process threading lock with a distributed synchronization primitive (such as Redis Redlock or a centralized token gateway) to guarantee single-flighted refreshes across all server instances.",
                "example_fix_code": None,
                "missing_context_needed": "Cannot safely generate exact code because the multi-process deployment architecture (e.g. Gunicorn configuration, Dockerfile, or Kubernetes manifest) and shared caching infrastructure (e.g. Redis client connection or Memcached URI) are not present in the submitted diff.",
                "has_sufficient_context": False
            }
        elif "sleep" in title_lower or "blocks worker" in title_lower or "thread starvation" in title_lower:
            return {
                "why_this_matters": "In synchronous WSGI web servers (such as Gunicorn with sync/gthread workers, Flask, or Django), worker threads are a strictly limited pool (typically 4-16 threads per process). When `time.sleep` blocks a worker thread for 1 to 7 seconds during external partner downtime, all available worker threads become blocked waiting on retries, resulting in complete denial-of-service for inbound API requests.",
                "where_problem_occurs": "services/payment_notifier.py: lines 45 and 56 at 'time.sleep(sleep_time)' inside the retry loop.",
                "recommended_approach": "Offload webhook delivery to an asynchronous background task queue (such as Celery, ARQ, or Redis Queue) with non-blocking exponential retry schedules, or use `asyncio.sleep()` within an asynchronous runtime.",
                "example_fix_code": """# Non-blocking asynchronous implementation with httpx and asyncio
import asyncio
import random
import httpx
import logging

logger = logging.getLogger(__name__)

async def dispatch_payment_webhook_async(event_payload: dict, webhook_url: str, max_retries: int = 3) -> bool:
    base_backoff_sec = 1.0
    headers = {"Content-Type": "application/json", "X-Event-Id": event_payload.get("id", "")}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.post(webhook_url, json=event_payload, headers=headers)
                if 200 <= response.status_code < 300:
                    logger.info("Payment notification delivered on attempt %d", attempt)
                    return True
                
                if response.status_code in (429, 500, 502, 503, 504):
                    # Full jitter exponential backoff
                    sleep_time = random.uniform(0.5, 1.0) * base_backoff_sec * (2 ** (attempt - 1))
                    logger.warning("HTTP %d retry in %.2fs (attempt %d/%d)", response.status_code, sleep_time, attempt, max_retries)
                    await asyncio.sleep(sleep_time)
                    continue
                else:
                    logger.error("Non-retryable HTTP %d from %s", response.status_code, webhook_url)
                    return False
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                sleep_time = random.uniform(0.5, 1.0) * base_backoff_sec * (2 ** (attempt - 1))
                logger.warning("Network error on attempt %d/%d: %s. Retrying in %.2fs...", attempt, max_retries, exc, sleep_time)
                await asyncio.sleep(sleep_time)
                
    return False""",
                "missing_context_needed": None,
                "has_sufficient_context": True
            }
        elif "jitter" in title_lower:
            return {
                "why_this_matters": "Without jitter, when an external API recovers from a temporary outage, all clients that experienced failures at roughly the same time will retry at identical intervals (1s, 2s, 4s). This creates synchronized spikes of traffic (thundering herds) that repeatedly crash the upstream partner endpoint.",
                "where_problem_occurs": "services/payment_notifier.py: lines 42 and 53 where sleep_time is calculated deterministically.",
                "recommended_approach": "Implement 'Full Jitter' exponential backoff by multiplying the exponential duration with a uniform random float between 0.5 and 1.0.",
                "example_fix_code": """import random

# Add randomized full jitter to decorrelate concurrent retries:
jitter_factor = random.uniform(0.5, 1.0)
sleep_time = jitter_factor * base_backoff_sec * (2 ** (attempt - 1))""",
                "missing_context_needed": None,
                "has_sufficient_context": True
            }
        elif "lock" in title_lower or "latency" in title_lower or "contention" in title_lower:
            return {
                "why_this_matters": "When worker threads queue up sequentially on an in-memory lock during upstream OAuth latency spikes, the entire worker pool can stall. If the OAuth server takes 5.0 seconds under load, 10 queued worker threads will wait up to 50 seconds cumulatively, causing thread pool exhaustion and user-facing 504 Gateway Timeouts.",
                "where_problem_occurs": "services/auth_client.py: inside get_valid_token(), lines 28-34 at 'with self._lock:' during double-checked locking.",
                "recommended_approach": "Implement a non-blocking lock acquisition strategy (self._lock.acquire(blocking=False)). If another worker thread is already in the process of refreshing the token, allow caller threads to serve traffic using the existing access token during a short grace period rather than blocking sequentially.",
                "example_fix_code": """# Non-blocking lock check with grace period fallback
def get_valid_token(self) -> str:
    # Check if within refresh window (30s before nominal expiry)
    if time.time() >= (self.expires_at - 30):
        # Attempt to acquire lock without blocking other concurrent workers
        if self._lock.acquire(blocking=False):
            try:
                if time.time() >= (self.expires_at - 30):
                    self._refresh_access_token()
            finally:
                self._lock.release()
        elif not self.access_token:
            # Cold start: first initialization must wait synchronously
            with self._lock:
                if not self.access_token:
                    self._refresh_access_token()
    return self.access_token""",
                "missing_context_needed": None,
                "has_sufficient_context": True
            }
        elif "race condition" in title_lower or "idempotency" in title_lower or "webhook" in title_lower:
            return {
                "why_this_matters": "Financial and data integrity risk. If payment providers deliver identical webhook events simultaneously (e.g. during network retries), both worker threads could execute the `select()` check before either transaction commits, causing the user account to be credited twice.",
                "where_problem_occurs": "billing/webhooks.py: lines 20-27 inside async with session.begin(): between the select(WebhookEvent) check and session.add().",
                "recommended_approach": "Rely on database-level unique constraints on `WebhookEvent.id` and catch `sqlalchemy.exc.IntegrityError` to safely acknowledge duplicate deliveries with HTTP 200 without duplicate credit execution.",
                "example_fix_code": """from sqlalchemy.exc import IntegrityError

event_id = event["id"]
async with get_db_session() as session:
    try:
        async with session.begin():
            # Insert WebhookEvent record immediately; DB unique constraint guarantees atomicity
            session.add(WebhookEvent(id=event_id, event_type=event["type"]))
            await session.flush()  # Forces immediate constraint check before billing logic
            
            if event["type"] == "payment_intent.succeeded":
                payment_intent = event["data"]["object"]
                user_id = payment_intent["metadata"]["user_id"]
                amount_credits = payment_intent["amount"] // 100
                
                user = await session.get(UserCredit, user_id)
                user.balance += amount_credits
    except IntegrityError:
        # Duplicate delivery was caught and safely rolled back by unique constraint
        return {"status": "already_processed"}

return {"status": "success"}""",
                "missing_context_needed": None,
                "has_sufficient_context": True
            }
        else:
            return {
                "why_this_matters": f"Production reliability impact: {issue.explanation}",
                "where_problem_occurs": "Within the modified logic block handling this code branch.",
                "recommended_approach": issue.suggested_action,
                "example_fix_code": None,
                "missing_context_needed": "Additional surrounding function signatures, caller definitions, or type annotations are required to safely construct an exact code replacement.",
                "has_sufficient_context": False
            }

    @classmethod
    def _clean_and_parse_json(cls, raw_text: str) -> Dict[str, Any]:
        """Strips markdown wrappers and safely parses JSON content."""
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n", "", text)
            text = re.sub(r"\n```$", "", text)
            text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            raise ModelResponseParseError(
                f"Model response did not contain valid JSON. Raw output preview: {raw_text[:300]}..."
            ) from exc

    @classmethod
    def _generate_mock_analysis(cls, code_change: str, context: Optional[str]) -> Dict[str, Any]:
        """Provides high-fidelity, grounded offline analysis strictly following the senior engineer reasoning schema."""
        code_lower = code_change.lower()
        now_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        if "dispatch_payment_webhook" in code_lower or "max_retries" in code_lower or "payment_notifier" in code_lower or "base_backoff_sec" in code_lower:
            return {
                "change_summary": "Implemented `dispatch_payment_webhook` with 3-attempt exponential backoff retry loop, HTTP status code filtering (retrying 429 and 5xx), connection timeout handling (5.0s), and event ID header propagation.",
                "change_purpose": "Ensure resilient delivery of mission-critical payment webhook notifications to external partner endpoints during transient network blips or partner server restarts.",
                "change_type": "resilience & external integration",
                "risk_level": "medium",
                "risk_explanation": "Observed: Implements automated retries with status code discrimination. Potential risk: Synchronous `time.sleep` in worker loop causes thread starvation during partner downtime; lack of randomized jitter could induce retry thundering herd against partner endpoints.",
                "potential_issues": [
                    {
                        "title": "Synchronous `time.sleep` Blocks Worker Thread During Retries",
                        "severity": "high",
                        "explanation": "Observed: `time.sleep(sleep_time)` is invoked synchronously on lines 45 and 56 within the retry loop. Potential risk: If the partner endpoint suffers extended downtime, each dispatch thread will block synchronously for up to 7+ seconds, starving the application's worker thread pool under concurrent load.",
                        "suggested_action": "Offload webhook dispatch to an asynchronous background task queue (e.g., Celery, RQ, or asyncio event loop) with non-blocking exponential retry schedules."
                    },
                    {
                        "title": "Missing Randomized Jitter in Exponential Backoff",
                        "severity": "medium",
                        "explanation": "Observed: Exponential backoff is calculated deterministically as `base_backoff_sec * (2 ** (attempt - 1))`. Potential risk: In the event of partner recovery after a transient outage, all waiting retries will fire simultaneously in synchronized thundering herd bursts.",
                        "suggested_action": "Add full jitter: `sleep_time = random.uniform(0.5, 1.0) * base_backoff_sec * (2 ** (attempt - 1))` to decorrelate concurrent retries."
                    },
                    {
                        "title": "Potential Non-Idempotent Duplicate Execution on Webhook Destination",
                        "severity": "low",
                        "explanation": "Observed: A generic POST request is retried on timeout. Potential risk: If the partner processed the payment event but failed to return an HTTP response before the 5.0s timeout, retrying could trigger duplicate downstream actions unless the partner enforces idempotency via `X-Event-Id`.",
                        "suggested_action": "Verify downstream partner documentation guarantees idempotency based on `X-Event-Id` before enabling retries for mutating operations."
                    }
                ],
                "edge_cases": [
                    "Partner endpoint responds with HTTP 429 Too Many Requests without Retry-After header",
                    "Network socket drops mid-transmission after partner successfully processed the payload",
                    "Invalid URL or DNS resolution failure raising requests.ConnectionError repeatedly"
                ],
                "test_scenarios": [
                    {
                        "test_name": "Transient HTTP 503 Retry & Eventual Success Verification",
                        "test_description": "Mock partner endpoint to return HTTP 503 on attempts 1 and 2, then HTTP 200 on attempt 3. Assert function logs warnings, executes backoff sleeps, returns True, and verifies payload integrity.",
                        "priority": "high"
                    },
                    {
                        "test_name": "Non-Retryable Client Error (HTTP 400) Fast Failure",
                        "test_description": "Mock partner to return HTTP 400 Bad Request; assert function terminates immediately on attempt 1 without retrying and returns False.",
                        "priority": "high"
                    },
                    {
                        "test_name": "Timeout Exhaustion & Fallback Return",
                        "test_description": "Mock partner to exceed 5.0s timeout across all 3 attempts; assert function handles requests.Timeout cleanly, exhausts retries, and returns False.",
                        "priority": "medium"
                    }
                ],
                "manager_update": "Added automated 3-attempt retry logic with exponential backoff for payment webhook notifications. This ensures critical payment events reach partners during temporary connectivity blips without manual intervention.",
                "ticket_update": "### Summary\nImplemented resilient payment webhook dispatcher with 3-attempt exponential backoff.\n\n### Changes\n- Added `dispatch_payment_webhook()` in `services/payment_notifier.py`\n- 3-attempt backoff (1s, 2s, 4s) on HTTP 429/5xx and socket timeouts\n- Immediate abort on 4xx client errors\n- Propagate `X-Event-Id` header for partner idempotency\n\n### Verification\n- [x] Verified retry on 503 and network timeout\n- [x] Verified non-retry on 400\n- [x] Verified header propagation",
                "technical_documentation": "The `dispatch_payment_webhook` function transmits JSON payloads to partner webhook URLs with up to 3 attempts. Exponential backoff operates at t = base * 2^(attempt-1). Retries trigger strictly on HTTP 429, 5xx status codes, and `requests.Timeout`/`ConnectionError`. Permanent 4xx errors return False immediately. Idempotency is supported via the `X-Event-Id` header.",
                "release_notes": "Improved payment webhook reliability with automatic retry handling for transient partner outages.",
                "shipping_readiness": "review recommended",
                "readiness_reason": "Review recommended: Retry logic and status code filtering are solid, but synchronous thread-blocking sleep should be migrated to background task workers before high-volume production rollout.",
                "ship_score": 78,
                "score_factor_explanation": "Synchronous blocking sleep in retry loop and lack of backoff jitter may cause worker thread pool starvation under external partner downtime.",
                "analyzed_at": now_ts
            }
        elif "lock" in code_lower or "token" in code_lower or "auth" in code_lower:
            return {
                "change_summary": "Added a threading.Lock with double-checked locking around token refresh logic, introduced a 30-second pre-expiry buffer window, added a 5.0s network timeout, and wrapped network failures in AuthRefreshError.",
                "change_purpose": "Prevent concurrent request bursts from triggering simultaneous token refresh requests (thundering herd) when access tokens expire under load.",
                "change_type": "bug fix & resilience",
                "risk_level": "medium",
                "risk_explanation": "Directly modifies core outbound API authentication. Observed: double-checked locking prevents concurrency storms within the process. Potential risk: lock contention could increase request latency if the OAuth refresh endpoint degrades.",
                "potential_issues": [
                    {
                        "title": "Lock Contention & Cascading Latency on OAuth Outage",
                        "severity": "medium",
                        "explanation": "Observed: A 5.0-second timeout is configured on line 42. Potential risk: If the OAuth server experiences high latency, multiple worker threads waiting on self._lock will block sequentially, temporarily inflating API response times.",
                        "suggested_action": "Canary checking recommended: Monitor p99 latency after release. Consider non-blocking or circuit-breaker patterns if thread density grows."
                    },
                    {
                        "title": "In-Memory Process Boundary on Concurrency Lock",
                        "severity": "low",
                        "explanation": "Observed: threading.Lock operates strictly in-memory within a single Python runtime. Potential risk: If deployed using multi-process worker pools (e.g. Gunicorn/Celery prefork), each process maintains its own independent lock and cache.",
                        "suggested_action": "Verify deployment topology. If scaling across multi-process containers, synchronize token caching via Redis."
                    }
                ],
                "edge_cases": [
                    "Token nominal expiry occurs while an outbound OAuth network request is actively in-flight",
                    "OAuth server responds with HTTP 400 invalid_grant during refresh token rotation, causing AuthRefreshError to bubble up",
                    "Host machine system clock skew drifting backwards causing expires_at comparison anomalies"
                ],
                "test_scenarios": [
                    {
                        "test_name": "Concurrent Token Refresh Double-Check Verification",
                        "test_description": "Spawn 20 parallel worker threads calling get_valid_token() with expired token state; assert OAuth refresh endpoint is invoked exactly once and all threads receive the valid token.",
                        "priority": "high"
                    },
                    {
                        "test_name": "Failure Path: OAuth Timeout & Exception Wrapping",
                        "test_description": "Mock OAuth endpoint to hang for 6 seconds; assert requests.Timeout triggers AuthRefreshError within 5.0s and self._lock is cleanly released.",
                        "priority": "high"
                    },
                    {
                        "test_name": "Refresh Token Rotation Verification",
                        "test_description": "Verify that when the OAuth server supplies a new refresh_token in the payload, the session updates its internal refresh_token property.",
                        "priority": "medium"
                    }
                ],
                "manager_update": "Resolved intermittent 401 unauthorized errors observed during high-traffic background synchronizations. The fix introduces thread-safe authentication token refreshing with zero breaking changes.",
                "ticket_update": "### Summary\nFixes intermittent 401 errors caused by concurrent token refresh storms when access tokens expire under load.\n\n### Changes\n- Implemented `threading.Lock` double-checked locking\n- Added 30s pre-expiration buffer window\n- Added 5s timeout and error handling for OAuth refresh\n\n### Verification\n- [x] Concurrent thread simulation passed\n- [x] Timeout handling verified",
                "technical_documentation": "The `AuthenticatedSession` class now guards access token renewals using double-checked locking. Token refresh triggers 30 seconds before nominal expiration. Network failures are normalized to `AuthRefreshError`.",
                "release_notes": "Improved session authentication reliability and resolved intermittent connection errors under high concurrent traffic.",
                "shipping_readiness": "ready",
                "readiness_reason": "Confirmed observation: Defensive concurrency pattern with explicit network timeouts and exception re-wrapping. No backward compatibility issues detected.",
                "ship_score": 88,
                "score_factor_explanation": "Thread-safe double-checked lock and timeout handling provide high safety, but requires latency monitoring under contention.",
                "analyzed_at": now_ts
            }
        elif "webhook" in code_lower or "stripe" in code_lower or "credit" in code_lower:
            return {
                "change_summary": "Wrapped Stripe webhook fulfillment in an atomic database transaction and implemented an idempotency check against the WebhookEvent ledger table.",
                "change_purpose": "Prevent double-crediting user accounts when payment webhooks are delivered multiple times by payment providers.",
                "change_type": "bug fix & data integrity",
                "risk_level": "high",
                "risk_explanation": "Directly impacts financial ledger entries and database transactions. Observed: Transaction wrapping guarantees atomicity for single requests. Potential risk: Concurrent duplicate webhook deliveries could race before transaction commit without database-level unique constraints.",
                "potential_issues": [
                    {
                        "title": "Potential Concurrent Insert Race Condition on WebhookEvent",
                        "severity": "high",
                        "explanation": "Observed: The code queries WebhookEvent with select() before executing session.add(). Potential risk: If identical webhook deliveries arrive concurrently before the initial transaction commits, both could evaluate existing as None, resulting in duplicate user credit allocation.",
                        "suggested_action": "Verify that WebhookEvent.id has a database-level UNIQUE constraint or Primary Key to force concurrent duplicate inserts to raise an integrity error."
                    },
                    {
                        "title": "Uncaught IntegrityError Handling on Duplicate Insertion",
                        "severity": "medium",
                        "explanation": "Observed: If the database enforces a unique constraint on WebhookEvent.id, a concurrent duplicate will trigger an unhandled SQLAlchemy IntegrityError and return HTTP 500, prompting Stripe to retry repeatedly.",
                        "suggested_action": "Catch sqlalchemy.exc.IntegrityError within the transaction block and return {'status': 'already_processed'} with HTTP 200 to acknowledge delivery."
                    }
                ],
                "edge_cases": [
                    "Duplicate webhook events received within milliseconds of each other during retry spikes",
                    "UserCredit record missing or locked during webhook execution",
                    "Stripe signature validation failure on malformed request headers"
                ],
                "test_scenarios": [
                    {
                        "test_name": "Webhook Idempotency Concurrent Replay Test",
                        "test_description": "Send identical payment_intent.succeeded webhook payload twice simultaneously; verify balance is incremented only once and second response returns already_processed.",
                        "priority": "high"
                    },
                    {
                        "test_name": "Failure Path: Transaction Rollback on Credit Error",
                        "test_description": "Simulate error while updating UserCredit; verify WebhookEvent is not marked as processed and transaction rolls back completely.",
                        "priority": "high"
                    }
                ],
                "manager_update": "Implemented safeguards in billing webhook processing to ensure customers are never double-credited when payment notifications are retried.",
                "ticket_update": "### Summary\nEnforces idempotency and transaction boundaries on Stripe webhook processing.\n\n### Changes\n- Persist processed event IDs in `WebhookEvent`\n- Wrap credit updates in `session.begin()`\n- Return early if event was already handled",
                "technical_documentation": "Payment webhook fulfillment is now executed within an explicit database transaction block. The `WebhookEvent` table acts as an idempotent ledger.",
                "release_notes": "Enhanced payment processing reliability and duplicate charge prevention.",
                "shipping_readiness": "review recommended",
                "readiness_reason": "Review recommended: While the transaction boundary and idempotency ledger are sound, database-level unique constraints and integrity error handling on race conditions must be confirmed before production release.",
                "ship_score": 65,
                "score_factor_explanation": "Elevated risk due to potential concurrent insert race conditions on billing ledger before unique constraint enforcement.",
                "analyzed_at": now_ts
            }
        else:
            return {
                "change_summary": "Configured database connection pooling parameters on SQLAlchemy engine, including pool recycle, pre-ping health verification, and environment variable configuration.",
                "change_purpose": "Eliminate intermittent database connection drops and operational errors during idle traffic periods.",
                "change_type": "performance & resilience",
                "risk_level": "low",
                "risk_explanation": "Configuration hardening on the database client engine. Observed: Does not modify query logic, database schema, or application contracts. Potential risk: If DATABASE_URL is unset or malformed in staging, the application will fail during engine initialization.",
                "potential_issues": [
                    {
                        "title": "Missing Environment Variable Fallback Validation",
                        "severity": "low",
                        "explanation": "Observed: DATABASE_URL defaults to a local production URI if unset in environment. Potential risk: If deployed to staging without DATABASE_URL, connection will attempt to reach the fallback URI and fail.",
                        "suggested_action": "Verify environment variable is configured across staging and production deployment manifests, and validate URI format on boot."
                    }
                ],
                "edge_cases": [
                    "Application boot when database server is temporarily unreachable",
                    "Database server closing idle connections after firewall or proxy timeout"
                ],
                "test_scenarios": [
                    {
                        "test_name": "Idle Connection Recovery Check",
                        "test_description": "Allow connection pool to idle past recycle threshold (1800s); issue query and verify pool_pre_ping automatically reconnects without raising OperationalError.",
                        "priority": "high"
                    }
                ],
                "manager_update": "Completed stability enhancement for backend database connections, preventing timeouts during quiet traffic windows.",
                "ticket_update": "### Summary\nConfigured database engine pooling parameters:\n- pool_recycle: 1800s\n- pool_pre_ping: True\n- pool_size: 20\n- max_overflow: 10",
                "technical_documentation": "SQLAlchemy engine is now initialized with proactive connection health checks (pre-ping) and a 30-minute recycling policy to prevent stale socket errors.",
                "release_notes": "Improved backend database connectivity resilience.",
                "shipping_readiness": "ready",
                "readiness_reason": "Confirmed observation: Low-risk configuration hardening with verified pre-ping health checks and connection recycling.",
                "ship_score": 92,
                "score_factor_explanation": "Low-risk defensive connection pool hardening with zero breaking API contract changes.",
                "analyzed_at": now_ts
            }
