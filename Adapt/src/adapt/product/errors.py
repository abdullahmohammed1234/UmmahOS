"""Product-layer errors. These wrap engine failures for the learner-facing boundary."""

from __future__ import annotations

from adapt.errors import AdaptError


class ProductError(AdaptError):
    """Base error for the Phase 4 product boundary."""

    code = "product_error"
    http_status = 500

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class SessionUnavailableError(ProductError):
    code = "session_unavailable"
    http_status = 404


class InvalidResponseError(ProductError):
    code = "invalid_response"
    http_status = 400


class ChallengeUnavailableError(ProductError):
    code = "challenge_unavailable"
    http_status = 409


class SessionCompleteError(ProductError):
    code = "session_complete"
    http_status = 409


class SubmissionError(ProductError):
    code = "submission_error"
    http_status = 500
