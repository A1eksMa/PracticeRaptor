"""SQLite implementation of IProblemRepository."""

import sqlite3
from pathlib import Path

from core.domain.enums import Category, Difficulty, ProblemStatus
from core.domain.problem import Problem, ProblemSummary
from core.persistence.records.problem_records import (
    EditorialRecord,
    ExampleRecord,
    ExplanationRecord,
    HintRecord,
    ProblemDescriptionRecord,
    ProblemRecord,
    TagRecord,
    TitleRecord,
)
from core.persistence.mappers.problem_mapper import (
    records_to_problem,
    records_to_problem_summary,
)


class SqliteProblemRepository:
    """SQLite-based problem repository.

    Reads data from SQLite database, converts to Records,
    then uses THE SAME mappers as JSON repository.

    This demonstrates the power of the Record abstraction:
    - Different storage backends
    - Same mapper logic
    - Same domain models
    """

    def __init__(self, db_path: Path):
        """Initialize repository.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection (lazy initialization)."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row  # Access by column name
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ========================================================
    # Private: Load records from SQLite
    # ========================================================

    def _load_problem_record(self, problem_id: int) -> ProblemRecord | None:
        """Load ProblemRecord by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM problems WHERE problem_id = ?",
            (problem_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        # Parse JSON arrays stored as strings
        import json

        return ProblemRecord(
            problem_id=row["problem_id"],
            difficulty=row["difficulty"],
            complexity=row["complexity"],
            categories=json.loads(row["categories"]),
            supported_languages=json.loads(row["supported_languages"]),
        )

    def _load_all_problem_records(self) -> list[ProblemRecord]:
        """Load all ProblemRecords."""
        import json

        cursor = self.conn.execute("SELECT * FROM problems")
        return [
            ProblemRecord(
                problem_id=row["problem_id"],
                difficulty=row["difficulty"],
                complexity=row["complexity"],
                categories=json.loads(row["categories"]),
                supported_languages=json.loads(row["supported_languages"]),
            )
            for row in cursor.fetchall()
        ]

    def _load_titles(self, problem_id: int) -> list[TitleRecord]:
        """Load TitleRecords for problem."""
        cursor = self.conn.execute(
            "SELECT * FROM titles WHERE problem_id = ?",
            (problem_id,),
        )
        return [
            TitleRecord(
                problem_id=row["problem_id"],
                language=row["language"],
                title=row["title"],
            )
            for row in cursor.fetchall()
        ]

    def _load_descriptions(self, problem_id: int) -> list[ProblemDescriptionRecord]:
        """Load DescriptionRecords for problem."""
        cursor = self.conn.execute(
            "SELECT * FROM descriptions WHERE problem_id = ?",
            (problem_id,),
        )
        return [
            ProblemDescriptionRecord(
                problem_id=row["problem_id"],
                language=row["language"],
                description=row["description"],
            )
            for row in cursor.fetchall()
        ]

    def _load_examples(self, problem_id: int) -> list[ExampleRecord]:
        """Load ExampleRecords for problem."""
        cursor = self.conn.execute(
            "SELECT * FROM examples WHERE problem_id = ?",
            (problem_id,),
        )
        return [
            ExampleRecord(
                example_id=row["example_id"],
                problem_id=row["problem_id"],
                input=row["input"],
                output=row["output"],
            )
            for row in cursor.fetchall()
        ]

    def _load_explanations(self, example_ids: list[int]) -> list[ExplanationRecord]:
        """Load ExplanationRecords for examples."""
        if not example_ids:
            return []

        placeholders = ",".join("?" * len(example_ids))
        cursor = self.conn.execute(
            f"SELECT * FROM explanations WHERE example_id IN ({placeholders})",
            example_ids,
        )
        return [
            ExplanationRecord(
                example_id=row["example_id"],
                language=row["language"],
                explanation=row["explanation"],
            )
            for row in cursor.fetchall()
        ]

    def _load_hints(self, problem_id: int) -> list[HintRecord]:
        """Load HintRecords for problem."""
        cursor = self.conn.execute(
            "SELECT * FROM hints WHERE problem_id = ? ORDER BY hint_index",
            (problem_id,),
        )
        return [
            HintRecord(
                problem_id=row["problem_id"],
                language=row["language"],
                hint_index=row["hint_index"],
                hint=row["hint"],
            )
            for row in cursor.fetchall()
        ]

    def _load_tags(self, problem_id: int) -> list[TagRecord]:
        """Load TagRecords for problem."""
        cursor = self.conn.execute(
            "SELECT * FROM tags WHERE problem_id = ?",
            (problem_id,),
        )
        return [
            TagRecord(
                problem_id=row["problem_id"],
                tag=row["tag"],
            )
            for row in cursor.fetchall()
        ]

    def _load_editorials(self, problem_id: int) -> list[EditorialRecord]:
        """Load EditorialRecords for problem."""
        cursor = self.conn.execute(
            "SELECT * FROM editorials WHERE problem_id = ?",
            (problem_id,),
        )
        return [
            EditorialRecord(
                problem_id=row["problem_id"],
                language=row["language"],
                editorial=row["editorial"],
            )
            for row in cursor.fetchall()
        ]

    # ========================================================
    # Public: IProblemRepository implementation
    # ========================================================

    def get_by_id(self, problem_id: int, locale: str = "en") -> Problem | None:
        """Get complete problem by ID.

        NOTE: Uses the SAME mapper as JsonProblemRepository!
        """
        # Load main record
        problem_rec = self._load_problem_record(problem_id)
        if problem_rec is None:
            return None

        # Load related records
        title_recs = self._load_titles(problem_id)
        description_recs = self._load_descriptions(problem_id)
        example_recs = self._load_examples(problem_id)
        example_ids = [e.example_id for e in example_recs]
        explanation_recs = self._load_explanations(example_ids)
        hint_recs = self._load_hints(problem_id)
        tag_recs = self._load_tags(problem_id)
        editorial_recs = self._load_editorials(problem_id)

        # Use THE SAME mapper as JSON repository
        return records_to_problem(
            problem_rec=problem_rec,
            title_recs=title_recs,
            description_recs=description_recs,
            example_recs=example_recs,
            explanation_recs=explanation_recs,
            hint_recs=hint_recs,
            tag_recs=tag_recs,
            editorial_recs=editorial_recs,
            status=ProblemStatus.NOT_STARTED,
        )

    def get_all_summaries(
        self,
        locale: str = "en",
        difficulty: Difficulty | None = None,
        category: Category | None = None,
        tag: str | None = None,
    ) -> list[ProblemSummary]:
        """Get lightweight problem list for display.

        Uses SQL for efficient filtering instead of loading all data.
        """
        import json

        # Build query with filters
        query = "SELECT * FROM problems WHERE 1=1"
        params: list = []

        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty.value)

        if category:
            # SQLite JSON: check if array contains value
            query += " AND categories LIKE ?"
            params.append(f'%"{category.value}"%')

        cursor = self.conn.execute(query, params)
        summaries = []

        for row in cursor.fetchall():
            problem_id = row["problem_id"]

            # Load minimal related data
            title_recs = self._load_titles(problem_id)
            tag_recs = self._load_tags(problem_id)

            # Filter by tag (if specified)
            if tag:
                tag_values = [t.tag for t in tag_recs]
                if tag not in tag_values:
                    continue

            problem_rec = ProblemRecord(
                problem_id=problem_id,
                difficulty=row["difficulty"],
                complexity=row["complexity"],
                categories=json.loads(row["categories"]),
                supported_languages=json.loads(row["supported_languages"]),
            )

            # Use THE SAME mapper
            summary = records_to_problem_summary(
                problem_rec=problem_rec,
                title_recs=title_recs,
                tag_recs=tag_recs,
                locale=locale,
                status=ProblemStatus.NOT_STARTED,
            )
            summaries.append(summary)

        return summaries

    def get_problem_ids(self) -> list[int]:
        """Get all problem IDs."""
        cursor = self.conn.execute("SELECT problem_id FROM problems")
        return [row["problem_id"] for row in cursor.fetchall()]

    def count(self) -> int:
        """Get total number of problems."""
        cursor = self.conn.execute("SELECT COUNT(*) as cnt FROM problems")
        return cursor.fetchone()["cnt"]
