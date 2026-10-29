"""
Custom exceptions for the Shipmate AI analysis layer.
"""
from __future__ import annotations


class ShipmateError(Exception):
    """Base exception for all Shipmate errors."""
    pass


class EmptyInputError(ShipmateError):
    """Raised when the submitted code change is empty."""
    pass


class MissingAPIKeyError(ShipmateError):
    """Raised when an API key is required but missing from environment variables."""
    pass


class RateLimitError(ShipmateError):
    """Raised when the LLM provider returns a rate limit (HTTP 429)."""
    pass


class APIConnectionError(ShipmateError):
    """Raised when network connection or HTTP request to the LLM provider fails."""
    pass


class ModelResponseParseError(ShipmateError):
    """Raised when the LLM response cannot be parsed into the expected Pydantic schema."""
    pass
