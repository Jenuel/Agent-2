"""
retry.py — Exponential-backoff retry helpers for Gemini API calls.

Handles google.api_core.exceptions.ResourceExhausted (HTTP 429) and any
exception whose message contains "429" or "RESOURCE_EXHAUSTED".
"""

import asyncio
import time
import random
from typing import Callable, TypeVar

from app.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

MAX_RETRIES   = 5
BASE_DELAY    = 2.0
MAX_DELAY     = 60.0
JITTER_FACTOR = 0.25


def _is_rate_limit(exc: Exception) -> bool:
    """Return True when *exc* looks like a 429 / RESOURCE_EXHAUSTED error."""
    name = type(exc).__name__
    msg  = str(exc)
    return (
        "ResourceExhausted" in name
        or "429"            in msg
        or "RESOURCE_EXHAUSTED" in msg
        or "rate limit"     in msg.lower()
        or "quota"          in msg.lower()
    )


def _backoff_delay(attempt: int) -> float:
    """Exponential backoff with ±jitter: BASE * 2^attempt, capped at MAX_DELAY."""
    delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
    jitter = delay * JITTER_FACTOR * (2 * random.random() - 1)   # ±25 %
    return max(0.0, delay + jitter)


# ── async wrapper ─────────────────────────────────────────────────────────────

async def call_with_retry_async(fn: Callable[[], T], label: str = "LLM call") -> T:
    """
    Call *fn()* (a zero-argument callable) up to MAX_RETRIES times,
    sleeping with exponential backoff whenever a 429 is returned.

    Raises the last exception if all retries are exhausted.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            return fn()
        except Exception as exc:
            if not _is_rate_limit(exc):
                raise                          # non-429 → propagate immediately

            if attempt == MAX_RETRIES:
                logger.error(
                    "[retry] %s: rate-limit persists after %d attempts — giving up.",
                    label, MAX_RETRIES,
                )
                raise

            delay = _backoff_delay(attempt)
            logger.warning(
                "[retry] %s: 429 received (attempt %d/%d) — retrying in %.1fs.",
                label, attempt + 1, MAX_RETRIES, delay,
            )
            await asyncio.sleep(delay)

    raise RuntimeError("Unreachable")   # satisfies type-checkers


# ── sync wrapper ──────────────────────────────────────────────────────────────

def call_with_retry_sync(fn: Callable[[], T], label: str = "LLM call") -> T:
    """
    Synchronous version of call_with_retry_async — uses time.sleep instead
    of asyncio.sleep.  Use this inside plain `def` functions.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            return fn()
        except Exception as exc:
            if not _is_rate_limit(exc):
                raise

            if attempt == MAX_RETRIES:
                logger.error(
                    "[retry] %s: rate-limit persists after %d attempts — giving up.",
                    label, MAX_RETRIES,
                )
                raise

            delay = _backoff_delay(attempt)
            logger.warning(
                "[retry] %s: 429 received (attempt %d/%d) — retrying in %.1fs.",
                label, attempt + 1, MAX_RETRIES, delay,
            )
            time.sleep(delay)

    raise RuntimeError("Unreachable")
