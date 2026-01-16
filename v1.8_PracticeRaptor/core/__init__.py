"""PracticeRaptor Core v1.8

Core layer with domain models, DTOs, and persistence.

Architecture:
- models/          Domain models (rich, with nested objects)
  - problem/       Problem-domain (static content)
  - user/          User-domain (dynamic content)
  - context/       Runtime context (WorkContext)
- dto/             Data Transfer Objects (for microservices)
- persistence/     Storage layer
  - records/       Flat storage structures
  - mappers/       Domain <-> Records conversion
- ports/           Interfaces (Protocols)
- services/        Business logic (pure functions)

Usage:
    from core.models import Problem, User, WorkContext
    from core.dto import ExecutionRequest, ExecutionResult
    from core.persistence import ProblemRecord, UserRecord
"""

__version__ = "1.8.0"
