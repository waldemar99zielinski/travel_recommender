from __future__ import annotations

from typing import Any


class ApiError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class DependencyNotConfiguredError(ApiError):
    def __init__(self, *, dependency_name: str) -> None:
        super().__init__(
            code="dependency_not_configured",
            message=f"Dependency '{dependency_name}' is not configured in app state.",
            status_code=500,
            details={"dependency_name": dependency_name},
        )


class SessionNotFoundError(ApiError):
    def __init__(self, *, user_id: str, session_id: str) -> None:
        super().__init__(
            code="session_not_found",
            message="Session was not found.",
            status_code=404,
            details={"user_id": user_id, "session_id": session_id},
        )


class ServiceNotReadyError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="service_not_ready",
            message="Service is not ready.",
            status_code=503,
            details=None,
        )
