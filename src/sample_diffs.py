"""
Curated, realistic sample git diffs for instant 1-click testing & hackathon demos.
"""
from __future__ import annotations
from typing import Dict, Any

# Primary Try-Demo Change (External API Request with 3-Attempt Retry Handling)
DEMO_CHANGE: Dict[str, Any] = {
    "title": "Payment Notifier: External API with 3-Attempt Exponential Backoff",
    "description": "Dispatches critical payment webhook notifications with 3-attempt exponential backoff, status code filtering, and error handling.",
    "context": "Feature: Added resilient payment webhook notification forwarder with 3-attempt exponential backoff. Resolves PAY-304.",
    "diff": """diff --git a/services/payment_notifier.py b/services/payment_notifier.py
index 4b8e21a..9f1a04b 100644
--- a/services/payment_notifier.py
+++ b/services/payment_notifier.py
@@ -10,6 +10,38 @@ import logging
 import time
 import requests
 
 logger = logging.getLogger(__name__)
 
+def dispatch_payment_webhook(event_payload: dict, webhook_url: str) -> bool:
+    \"\"\"Dispatches a critical payment event notification with up to 3 retries.\"\"\"
+    max_retries = 3
+    base_backoff_sec = 1.0
+    
+    for attempt in range(1, max_retries + 1):
+        try:
+            response = requests.post(
+                webhook_url,
+                json=event_payload,
+                headers={"Content-Type": "application/json", "X-Event-Id": event_payload.get("id", "")},
+                timeout=5.0
+            )
+            # Consider any 2xx response a successful delivery
+            if 200 <= response.status_code < 300:
+                logger.info("Payment notification delivered successfully on attempt %d", attempt)
+                return True
+            
+            # Retry on transient server errors (5xx) or rate limit (429)
+            if response.status_code in (429, 500, 502, 503, 504):
+                sleep_time = base_backoff_sec * (2 ** (attempt - 1))
+                logger.warning("Delivery failed with HTTP %d. Retrying in %.1fs (attempt %d/%d)...",
+                               response.status_code, sleep_time, attempt, max_retries)
+                time.sleep(sleep_time)
+                continue
+            else:
+                # Permanent client failure (4xx) - abort retry
+                logger.error("Non-retryable HTTP error %d received from %s", response.status_code, webhook_url)
+                return False
+                
+        except (requests.Timeout, requests.ConnectionError) as exc:
+            sleep_time = base_backoff_sec * (2 ** (attempt - 1))
+            logger.warning("Network error '%s' on attempt %d/%d. Retrying in %.1fs...",
+                           exc, attempt, max_retries, sleep_time)
+            time.sleep(sleep_time)
+        except Exception as exc:
+            logger.error("Unexpected exception during webhook dispatch: %s", exc)
+            return False
+            
+    logger.error("Exceeded %d retry attempts for webhook %s", max_retries, webhook_url)
+    return False
"""
}

SAMPLE_DIFFS: Dict[str, Dict[str, Any]] = {
    "demo_retry_api": DEMO_CHANGE,
    "auth_race_condition": {
        "title": "Auth: Refresh Token Expiry & Race Condition Fix",
        "description": "Fixes 401 unauthorized errors when multiple concurrent API requests trigger simultaneous refresh token rotations.",
        "context": "Resolves JIRA-4219: Intermittent 401 errors during background sync when access tokens expire under load.",
        "diff": """diff --git a/services/auth_client.py b/services/auth_client.py
index a7f891b..d43e12c 100644
--- a/services/auth_client.py
+++ b/services/auth_client.py
@@ -14,6 +14,8 @@ import requests
 import time
 import logging
+import threading
 
 logger = logging.getLogger(__name__)
 
@@ -23,6 +25,7 @@ class AuthenticatedSession:
         self.access_token = None
         self.refresh_token = initial_refresh_token
         self.expires_at = 0
+        self._lock = threading.Lock()
 
     def get_valid_token(self) -> str:
-        if time.time() >= self.expires_at:
-            self._refresh_access_token()
-        return self.access_token
+        # Double-checked locking to prevent concurrent token refresh storms
+        if time.time() >= (self.expires_at - 30):
+            with self._lock:
                 if time.time() >= (self.expires_at - 30):
                     self._refresh_access_token()
         return self.access_token
 
     def _refresh_access_token(self):
         logger.info("Refreshing access token via OAuth server...")
-        resp = requests.post(
-            "https://auth.company.internal/oauth/token",
-            data={"grant_type": "refresh_token", "refresh_token": self.refresh_token}
-        )
-        data = resp.json()
-        self.access_token = data["access_token"]
-        self.expires_at = time.time() + data["expires_in"]
+        try:
+            resp = requests.post(
+                "https://auth.company.internal/oauth/token",
+                data={"grant_type": "refresh_token", "refresh_token": self.refresh_token},
+                timeout=5.0
+            )
+            resp.raise_for_status()
+            data = resp.json()
+            self.access_token = data["access_token"]
+            # Rotate refresh token if provided
+            if "refresh_token" in data:
+                self.refresh_token = data["refresh_token"]
+            # Give 30s buffer before nominal expiration
+            self.expires_at = time.time() + data.get("expires_in", 3600)
+        except requests.RequestException as exc:
+            logger.error("Token refresh failed: %s", exc)
+            raise AuthRefreshError("Unable to refresh auth credentials") from exc
"""
    },
    "stripe_webhook_idempotency": {
        "title": "Payments: Stripe Webhook Idempotency & DB Transaction",
        "description": "Wraps subscription fulfillment in a database transaction and enforces idempotency key locking to prevent double-crediting.",
        "context": "Fixes billing duplicate credits observed during Stripe retry spikes on network timeouts.",
        "diff": """diff --git a/billing/webhooks.py b/billing/webhooks.py
index b11c990..e84a201 100644
--- a/billing/webhooks.py
+++ b/billing/webhooks.py
@@ -1,6 +1,8 @@
 from fastapi import APIRouter, Header, HTTPException, Request
 import stripe
+from sqlalchemy import select
 from db import get_db_session
+from db.models import WebhookEvent, UserCredit
 
 router = APIRouter()
 
@@ -15,10 +17,21 @@ async def stripe_webhook(request: Request, stripe_signature: str = Header(...)):
     except (ValueError, stripe.error.SignatureVerificationError):
         raise HTTPException(status_code=400, detail="Invalid signature")
 
-    if event["type"] == "payment_intent.succeeded":
-        payment_intent = event["data"]["object"]
-        user_id = payment_intent["metadata"]["user_id"]
-        amount_credits = payment_intent["amount"] // 100
-        # Credit user credits
-        add_user_credits(user_id, amount_credits)
+    event_id = event["id"]
+    async with get_db_session() as session:
+        async with session.begin():
+            # Check if event was already processed
+            existing = await session.scalar(select(WebhookEvent).where(WebhookEvent.id == event_id))
+            if existing:
+                return {"status": "already_processed"}
+            
+            # Mark as processed immediately within transaction
+            session.add(WebhookEvent(id=event_id, event_type=event["type"]))
+            
+            if event["type"] == "payment_intent.succeeded":
+                payment_intent = event["data"]["object"]
+                user_id = payment_intent["metadata"]["user_id"]
+                amount_credits = payment_intent["amount"] // 100
+                
+                user = await session.get(UserCredit, user_id)
+                user.balance += amount_credits
 
     return {"status": "success"}
"""
    },
    "db_connection_pooling": {
        "title": "Database: Connection Pooling & Automatic Reconnect",
        "description": "Adds pool recycling, pre-ping health check, and max overflow settings to prevent database connection exhaustion under burst traffic.",
        "context": "Resolves production 500 error spike: 'OperationalError: MySQL server has gone away' after idle timeouts.",
        "diff": """diff --git a/core/database.py b/core/database.py
index 45f7823..90c8a11 100644
--- a/core/database.py
+++ b/core/database.py
@@ -1,5 +1,6 @@
 from sqlalchemy import create_engine
 from sqlalchemy.orm import sessionmaker
+import os
 
-DATABASE_URL = "postgresql://app:secret@db:5432/production"
-engine = create_engine(DATABASE_URL)
+DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:secret@db:5432/production")
+
+engine = create_engine(
+    DATABASE_URL,
+    pool_size=20,
+    max_overflow=10,
+    pool_timeout=30,
+    pool_recycle=1800,  # Recycle connection every 30 mins to avoid idle disconnects
+    pool_pre_ping=True   # Check connection liveness before checking out from pool
+)
 
 SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""
    }
}
