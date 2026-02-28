class ApplicationError(Exception):
    """Base error for application layer."""


class NotFoundError(ApplicationError):
    """Raised when an aggregate is not found."""


class AccessDeniedError(ApplicationError):
    """Raised when policy denies the action."""


class InvariantViolationError(ApplicationError):
    """Raised when domain invariants are violated."""
