"""JSON implementation of IProblemRepository."""

import json
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


class JsonProblemRepository:
    """JSON file-based problem repository.

    Reads data from separate JSON files, converts to Records,
    then uses mappers to build Domain models.

    Structure:
        data/json/
        ├── problems.json
        ├── titles.json
        ├── descriptions.json
        └── ...
    """

    def __init__(self, data_dir: Path):
        """Initialize repository.

        Args:
            data_dir: Path to directory containing JSON files
        """
        self.data_dir = data_dir
        self._cache: dict[str, list] = {}

    # ========================================================
    # Private: JSON loading
    # ========================================================

    def _load_json(self, filename: str) -> list[dict]:
        """Load JSON file with caching."""
        if filename not in self._cache:
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    self._cache[filename] = json.load(f)
            else:
                self._cache[filename] = []
        return self._cache[filename]

    def _clear_cache(self) -> None:
        """Clear cached data (for testing or refresh)."""
        self._cache.clear()

    # ========================================================
    # Private: Load records by problem_id
    # ========================================================

    def _load_problem_record(self, problem_id: int) -> ProblemRecord | None:
        """Load ProblemRecord by ID."""
        for data in self._load_json("problems.json"):
            if data["problem_id"] == problem_id:
                return ProblemRecord(**data)
        return None

    def _load_all_problem_records(self) -> list[ProblemRecord]:
        """Load all ProblemRecords."""
        return [ProblemRecord(**data) for data in self._load_json("problems.json")]

    def _load_titles(self, problem_id: int) -> list[TitleRecord]:
        """Load TitleRecords for problem."""
        return [
            TitleRecord(**data)
            for data in self._load_json("titles.json")
            if data["problem_id"] == problem_id
        ]

    def _load_descriptions(self, problem_id: int) -> list[ProblemDescriptionRecord]:
        """Load DescriptionRecords for problem."""
        return [
            ProblemDescriptionRecord(**data)
            for data in self._load_json("descriptions.json")
            if data["problem_id"] == problem_id
        ]

    def _load_examples(self, problem_id: int) -> list[ExampleRecord]:
        """Load ExampleRecords for problem."""
        return [
            ExampleRecord(**data)
            for data in self._load_json("examples.json")
            if data["problem_id"] == problem_id
        ]

    def _load_explanations(self, example_ids: list[int]) -> list[ExplanationRecord]:
        """Load ExplanationRecords for examples."""
        return [
            ExplanationRecord(**data)
            for data in self._load_json("explanations.json")
            if data["example_id"] in example_ids
        ]

    def _load_hints(self, problem_id: int) -> list[HintRecord]:
        """Load HintRecords for problem."""
        return [
            HintRecord(**data)
            for data in self._load_json("hints.json")
            if data["problem_id"] == problem_id
        ]

    def _load_tags(self, problem_id: int) -> list[TagRecord]:
        """Load TagRecords for problem."""
        return [
            TagRecord(**data)
            for data in self._load_json("tags.json")
            if data["problem_id"] == problem_id
        ]

    def _load_editorials(self, problem_id: int) -> list[EditorialRecord]:
        """Load EditorialRecords for problem."""
        return [
            EditorialRecord(**data)
            for data in self._load_json("editorials.json")
            if data["problem_id"] == problem_id
        ]

    # ========================================================
    # Public: IProblemRepository implementation
    # ========================================================

    def get_by_id(self, problem_id: int, locale: str = "en") -> Problem | None:
        """Get complete problem by ID."""
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

        # Use mapper to build domain model
        return records_to_problem(
            problem_rec=problem_rec,
            title_recs=title_recs,
            description_recs=description_recs,
            example_recs=example_recs,
            explanation_recs=explanation_recs,
            hint_recs=hint_recs,
            tag_recs=tag_recs,
            editorial_recs=editorial_recs,
            status=ProblemStatus.NOT_STARTED,  # TODO: load from user progress
        )

    def get_all_summaries(
        self,
        locale: str = "en",
        difficulty: Difficulty | None = None,
        category: Category | None = None,
        tag: str | None = None,
    ) -> list[ProblemSummary]:
        """Get lightweight problem list for display."""
        summaries = []

        for problem_rec in self._load_all_problem_records():
            # Apply filters
            if difficulty and problem_rec.difficulty != difficulty.value:
                continue
            if category and category.value not in problem_rec.categories:
                continue

            # Load minimal related data
            title_recs = self._load_titles(problem_rec.problem_id)
            tag_recs = self._load_tags(problem_rec.problem_id)

            # Filter by tag
            if tag:
                tag_values = [t.tag for t in tag_recs]
                if tag not in tag_values:
                    continue

            # Use mapper to build summary
            summary = records_to_problem_summary(
                problem_rec=problem_rec,
                title_recs=title_recs,
                tag_recs=tag_recs,
                locale=locale,
                status=ProblemStatus.NOT_STARTED,  # TODO: load from user progress
            )
            summaries.append(summary)

        return summaries

    def get_problem_ids(self) -> list[int]:
        """Get all problem IDs."""
        return [rec.problem_id for rec in self._load_all_problem_records()]

    def count(self) -> int:
        """Get total number of problems."""
        return len(self._load_all_problem_records())
