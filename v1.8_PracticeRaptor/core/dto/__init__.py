"""Data Transfer Objects for microservice communication.

DTOs are flat, serializable structures for API communication.
Used primarily for executor service requests/responses.
"""

from .execution import (
    ExecutionRequest,
    ExecutionResult,
    TestResultDTO,
    build_execution_request,
)

__all__ = [
    "ExecutionRequest",
    "ExecutionResult",
    "TestResultDTO",
    "build_execution_request",
]
