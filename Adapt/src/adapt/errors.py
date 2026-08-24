"""ADAPT error types. Invalid data must not become a confident learner state."""


class AdaptError(Exception):
    """Base error for the ADAPT prototype."""


class InvalidLearnerStateError(AdaptError):
    """Learner state is missing required fields or has out-of-range values."""


class InvalidLearnerResponseError(AdaptError):
    """Learner response is missing required fields or has invalid values."""


class InvalidEvidenceError(AdaptError):
    """Evidence object is malformed or uses an unsupported value."""


class InvalidChallengeError(AdaptError):
    """Challenge is missing or malformed."""


class MissingChallengeError(AdaptError):
    """A required challenge was not provided."""


class InvalidAdaptationDecisionError(AdaptError):
    """Adaptation decision is missing, unknown, or lacks an evidence trail."""


class InvalidStrategyStateError(AdaptError):
    """Strategy state is missing required fields or has out-of-range values."""


class InvalidStrategyDecisionError(AdaptError):
    """Strategy decision is missing, unknown, or lacks an evidence trail."""


class InvalidSessionError(AdaptError):
    """Tutor session is missing, malformed, or cannot be restored."""


class SessionNotFoundError(InvalidSessionError):
    """Requested tutor session does not exist."""
