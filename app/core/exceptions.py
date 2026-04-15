from __future__ import annotations


class LostFoundBaseError(Exception):
    """Root exception for all application-level errors."""


# ── Scraping ─────────────────────────────────────────────────────────────────

class ScraperError(LostFoundBaseError):
    """Raised when a scraping provider call fails."""


class ScraperRateLimitError(ScraperError):
    """Raised when a provider returns a 429 / rate-limit signal."""


class ScraperBlockedError(ScraperError):
    """Raised when the scraper detects it has been blocked."""


class ScraperTimeoutError(ScraperError):
    """Raised on unrecoverable timeout from the scraping provider."""


# ── LLM / Processing ─────────────────────────────────────────────────────────

class LLMError(LostFoundBaseError):
    """Raised when a Gemini / DSPy call fails."""


class LLMRateLimitError(LLMError):
    """Raised on 429 from Gemini — triggers exponential back-off."""


class LLMContextOverflowError(LLMError):
    """Raised when post text exceeds model context window."""


class ProcessingError(LostFoundBaseError):
    """Raised when the DSPy pipeline fails to produce a valid output."""


# ── Database ─────────────────────────────────────────────────────────────────

class DatabaseError(LostFoundBaseError):
    """Raised on unexpected database errors."""


class DuplicatePostError(DatabaseError):
    """Raised when a post already exists (soft-handled via ON CONFLICT)."""


# ── API ───────────────────────────────────────────────────────────────────────

class NotFoundError(LostFoundBaseError):
    """Raised when a requested resource does not exist."""


class ValidationError(LostFoundBaseError):
    """Raised when request data fails domain validation."""
