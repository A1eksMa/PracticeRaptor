# PracticeRaptor v1.6 - Enhanced Domain Models

**Status:** In Development
**Stage:** 1.6 - CLI Enhancement with User Management

## What's New in v1.6

### 🎯 Core Changes

#### 1. **Separation of Concerns: Language Types**
- **Language** - Interface language (EN, RU) for UI
- **ProgrammingLanguage** - Code language (Python, Java) for solutions

#### 2. **Normalized Multilingual Data**
Instead of dictionaries:
```python
# ❌ v1.5 approach
title: LocalizedText = {"en": "Two Sum", "ru": "Два числа"}

# ✅ v1.6 approach
Title(problem_id=1, language=Language.EN, title="Two Sum")
Title(problem_id=1, language=Language.RU, title="Два числа")
```

Benefits:
- Database-friendly (proper normalization)
- Easy to query by language
- Scalable for adding new languages

#### 3. **Problem Entity Split (Lazy Loading)**

Problems are split into 3 parts:

| Entity | Purpose | When to Load |
|--------|---------|--------------|
| **Problem** | Minimal (id, status) | Always |
| **ProblemSelector** | Filtering metadata (difficulty, tags, categories) | Problem List |
| **ProblemDescription** | Full content (description, examples, hints) | Problem Details |

This enables:
- Fast list rendering (lightweight data)
- Efficient filtering without loading descriptions
- Better performance with hundreds of problems

#### 4. **Solution Architecture**

**Solution** - Working object in memory:
- Initially contains: signature, canonical solutions, all tests
- User fills: `code` field
- Two test modes:
  - `test_cases: tuple[int, ...]` - indices for **quick check** (examples)
  - `tests: tuple[TestCase, ...]` - **all tests** for submission

**Draft** - Snapshot of Solution:
- Saved on events: code check, exit, manual save
- Contains timestamps for versioning
- Enables auto-save functionality

#### 5. **TestCase as Executable Code**

Tests are language-specific executable code:

```python
# Python test
TestCase(
    test_case_id=1,
    problem_id=1,
    programming_language=ProgrammingLanguage.PYTHON,
    test='assert solution([2, 7, 11, 15], 9) == [0, 1]'
)

# Java test
TestCase(
    test_case_id=1,
    problem_id=1,
    programming_language=ProgrammingLanguage.JAVA,
    test='assertEquals(Arrays.asList(0, 1), solution(new int[]{2, 7, 11, 15}, 9));'
)
```

Execution handled by language-specific microservices.

#### 6. **Full User Management**

```python
@dataclass(frozen=True)
class User:
    user_id: int
    user_name: str
    hash_password: str  # Hashed
    email: str

@dataclass(frozen=True)
class Settings:
    user_id: int
    language: Language
    programming_language: ProgrammingLanguage
    text_editor: TextEditor
    # Current selections (session state)
    select_problem_id: int | None
    select_difficulty: Difficulty | None
    select_tags: tuple[str, ...]
    select_category: Category | None
    select_status: Status | None
```

Replaces anonymous auth from v1.5 with proper authentication.

#### 7. **Extended Enumerations**

**Category** (17 categories):
```
Array, String, Hash Table, Two Pointers, Linked List, Stack, Queue,
Tree, Graph, Binary Search, Dynamic Programming, Greedy, Backtracking,
Bit Manipulation, Math, Sorting, Heap
```

**Complexity** (full Big O notation):
```
O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2ⁿ), O(n!)
```

---

## Domain Model Structure

### Enumerations
1. `Language` - Interface languages
2. `ProgrammingLanguage` - Programming languages
3. `TextEditor` - Text editors
4. `Difficulty` - Problem difficulty
5. `Category` - Problem categories
6. `Complexity` - Algorithmic complexity
7. `Status` - User progress status
8. `SubmissionStatus` - Execution result status

### Value Objects

**Localized Content:**
- `Title` - Problem title
- `Description` - Problem description
- `Editorial` - Solution explanation
- `Explanation` - Example explanation
- `Hint` - Problem hint

**Language-Specific:**
- `Signature` - Function signature
- `CanonicalSolution` - Reference solution
- `Tag` - Flexible tag

### Entities

**User Management:**
- `User` - User account
- `Settings` - User preferences and session

**Problem (Lightweight):**
- `Problem` - Minimal info
- `ProblemSelector` - Filtering metadata

**Problem (Heavyweight):**
- `ProblemDescription` - Full content
- `Example` - Input/output example

**Solution:**
- `Solution` - Working specification + user code
- `Draft` - Saved snapshot
- `TestCase` - Executable test

**Execution:**
- `Execution` - Execution result
- `TestResult` - Single test result
- `Submission` - Successful submission record

---

## Usage Examples

### Loading Problem List
```python
# Load lightweight data only
problems = problem_repo.get_all()  # Returns Problem + ProblemSelector
for problem in problems:
    title = title_repo.get(problem.problem_id, user.settings.language)
    print(f"{problem.problem_id}. {title.title} [{problem.difficulty}]")
```

### Loading Problem Details
```python
# Load full description when user selects problem
description = description_repo.get(problem_id, user.settings.language)
examples = example_repo.get_all(problem_id)
hints = hint_repo.get_all(problem_id, user.settings.language)
```

### Working with Solution
```python
# Create solution from specification
solution = Solution(
    problem_id=1,
    programming_language=ProgrammingLanguage.PYTHON,
    function_signature=signature,
    canonical_solutions=canonical_solutions,
    code="",  # User will fill this
    tests=all_tests,
    test_cases=(0, 1, 2)  # Run only first 3 tests for quick check
)

# User writes code
solution = replace(solution, code=user_code)

# Quick check (examples only)
quick_result = executor.run(solution, solution.test_cases)

# Full submission (all tests)
full_result = executor.run(solution, range(len(solution.tests)))

# Save draft
draft = Draft(solution=solution, created_at=now, updated_at=now)
draft_repo.save(draft)
```

---

## Architecture Principles

1. **Immutability** - All dataclasses are frozen
2. **Normalization** - No nested dictionaries for i18n
3. **Lazy Loading** - Load only what's needed
4. **Type Safety** - Full mypy support
5. **Separation** - Clear distinction between interface language and programming language
6. **Flexibility** - Categories (enum) + Tags (free-form)

---

## Migration from v1.5

| v1.5 | v1.6 | Change |
|------|------|--------|
| `Language` | `ProgrammingLanguage` | Renamed |
| `LocalizedText` | `Title`, `Description`, etc. | Normalized |
| `Problem` (monolithic) | `Problem` + `ProblemSelector` + `ProblemDescription` | Split |
| `Solution` (canonical) | `CanonicalSolution` | Renamed |
| `TestCase` (dict) | `TestCase` (executable code) | Redesigned |
| `User` (anonymous) | `User` (auth) | Enhanced |

---

## Next Steps

- [ ] Implement repositories for new models
- [ ] Create migration scripts from v1.5 data format
- [ ] Update CLI to use new authentication
- [ ] Implement lazy loading in UI
- [ ] Add multi-language support to CLI
