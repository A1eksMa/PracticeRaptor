"""Example: Using Problem repositories.

Demonstrates that both JSON and SQLite repositories:
- Use the same interface
- Use the same mappers
- Return the same domain models
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
JSON_DIR = BASE_DIR / "data" / "json"
SQLITE_DB = BASE_DIR / "data" / "sqlite" / "practiceraptor.db"


def example_json_repository():
    """Example: Using JSON repository."""
    from adapters.storage.json import JsonProblemRepository

    repo = JsonProblemRepository(JSON_DIR)

    # Get problem list
    print("=== JSON Repository ===")
    print(f"Total problems: {repo.count()}")

    summaries = repo.get_all_summaries(locale="ru")
    for s in summaries:
        print(f"  [{s.difficulty.value}] {s.title} - tags: {s.tags}")

    # Get full problem
    problem = repo.get_by_id(1, locale="ru")
    if problem:
        print(f"\nProblem: {problem.title.get('ru')}")
        print(f"Description: {problem.description.get('ru')[:50]}...")
        print(f"Examples: {len(problem.examples)}")
        print(f"Hints: {len(problem.hints)}")


def example_sqlite_repository():
    """Example: Using SQLite repository."""
    from adapters.storage.sqlite import SqliteProblemRepository

    # Note: Need to create DB first:
    # sqlite3 practiceraptor.db < schema.sql
    # sqlite3 practiceraptor.db < seed.sql

    if not SQLITE_DB.exists():
        print("=== SQLite Repository ===")
        print("Database not found. Create it with:")
        print(f"  cd {SQLITE_DB.parent}")
        print("  sqlite3 practiceraptor.db < schema.sql")
        print("  sqlite3 practiceraptor.db < seed.sql")
        return

    repo = SqliteProblemRepository(SQLITE_DB)

    print("=== SQLite Repository ===")
    print(f"Total problems: {repo.count()}")

    summaries = repo.get_all_summaries(locale="ru")
    for s in summaries:
        print(f"  [{s.difficulty.value}] {s.title} - tags: {s.tags}")

    # Get full problem - SAME domain model as JSON!
    problem = repo.get_by_id(1, locale="ru")
    if problem:
        print(f"\nProblem: {problem.title.get('ru')}")
        print(f"Description: {problem.description.get('ru')[:50]}...")
        print(f"Examples: {len(problem.examples)}")
        print(f"Hints: {len(problem.hints)}")

    repo.close()


def example_dependency_injection():
    """Example: Repository as dependency (DI pattern)."""
    from core.ports.repositories import IProblemRepository
    from adapters.storage.json import JsonProblemRepository

    def get_problem_title(repo: IProblemRepository, problem_id: int, locale: str) -> str:
        """Service function that accepts any repository implementation."""
        problem = repo.get_by_id(problem_id, locale)
        if problem:
            return problem.title.get(locale)
        return "Not found"

    # Can pass any implementation
    json_repo = JsonProblemRepository(JSON_DIR)
    title = get_problem_title(json_repo, 1, "ru")
    print(f"\n=== DI Example ===")
    print(f"Title from JSON repo: {title}")

    # Same function works with SQLite repo
    # sqlite_repo = SqliteProblemRepository(SQLITE_DB)
    # title = get_problem_title(sqlite_repo, 1, "ru")


if __name__ == "__main__":
    example_json_repository()
    print()
    example_sqlite_repository()
    example_dependency_injection()
