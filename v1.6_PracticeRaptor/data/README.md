# Data Directory

**Version:** 1.6
**Format:** Normalized JSON (foundation for relational database)

## Quick Overview

This directory contains **normalized data** split into 17 JSON files representing a relational schema.

### Structure

```
data/
├── SCHEMA.md                    # 📖 Full documentation with ER diagram
│
├── problems/                    # Problem data (13 files)
│   ├── problems.json            # Core registry
│   ├── problem_selectors.json   # Metadata for filtering
│   ├── problem_descriptions.json # Heavy metadata
│   ├── titles.json              # Localized titles
│   ├── descriptions.json        # Localized descriptions
│   ├── editorials.json          # Localized editorials
│   ├── hints.json               # Localized hints
│   ├── examples.json            # Examples (input/output)
│   ├── explanations.json        # Localized explanations
│   ├── signatures.json          # Function signatures
│   ├── canonical_solutions.json # Reference solutions
│   ├── test_cases.json          # Executable test code
│   └── tags.json                # Flexible tags
│
├── users/                       # User management (2 files)
│   ├── users.json               # User accounts
│   └── settings.json            # User preferences
│
├── drafts/                      # Work in progress (1 file)
│   └── drafts.json              # Auto-saved code
│
└── submissions/                 # Source of truth (1 file)
    └── submissions.json         # Successful solutions → stats
```

## Key Concepts

### 1. Normalized Structure
Each entity has its own file(s). No nested dictionaries.

**Example:** Problem titles
```json
// ❌ OLD (v1.5): Nested dictionary
{"title": {"en": "Two Sum", "ru": "Два числа"}}

// ✅ NEW (v1.6): Separate records
{"problem_id": 1, "language": "en", "title": "Two Sum"}
{"problem_id": 1, "language": "ru", "title": "Два числа"}
```

### 2. Lazy Loading
Problems split into 3 parts:
- **problems.json** - Always loaded (just IDs)
- **problem_selectors.json** - For list view (metadata)
- **problem_descriptions.json** - For detail view (heavy data)

### 3. Statistics from Submissions
No separate Progress table. All stats computed from `submissions.json`:
- Solved problems → `SELECT DISTINCT problem_id WHERE user_id=?`
- Best time → `SELECT MIN(total_time_ms) WHERE user_id=? AND problem_id=?`
- Streak → Count consecutive days with submissions

### 4. Executable Test Code
Tests are language-specific code strings:
```json
{
  "test_case_id": 1,
  "programming_language": "python3",
  "test": "assert two_sum([2, 7, 11, 15], 9) == [0, 1]"
}
```

Executed by language-specific microservices.

## Sample Data

Currently includes:
- **3 problems:** Two Sum, Reverse String, Valid Palindrome
- **2 users:** alexei, demo_user
- **3 drafts:** Work in progress code
- **5 submissions:** Successful solutions

All problems have:
- ✅ English & Russian translations
- ✅ Python3 support (Problem 1 also has Java)
- ✅ Examples, hints, editorials
- ✅ Multiple canonical solutions
- ✅ Executable test cases

## Documentation

📖 **See [SCHEMA.md](./SCHEMA.md) for:**
- Complete ER diagram
- Table descriptions
- SQL migration examples
- Domain model ↔ Table mapping
- Query patterns
- Architectural decisions

## Migration Path

```
Stage 1.6 (Now)    → JSON files (this structure)
Stage 1.7          → SQLite (same schema)
Stage 1.7+         → PostgreSQL (production)
```

The JSON structure directly maps to SQL tables.

## Usage

### Loading Problem List
```python
# 1. Load minimal data
problems = load_json("problems/problems.json")
selectors = load_json("problems/problem_selectors.json")
titles = load_json("problems/titles.json")

# 2. Filter by difficulty
easy_problems = [s for s in selectors if s["difficulty"] == "easy"]

# 3. Get title for user's language
title = next(t for t in titles
             if t["problem_id"] == 1 and t["language"] == "ru")
```

### Loading Problem Details
```python
# Load heavy data only when user selects problem
description = load_json("problems/descriptions.json")
examples = load_json("problems/examples.json")
hints = load_json("problems/hints.json")

# Filter by problem_id and language
problem_desc = next(d for d in description
                   if d["problem_id"] == 1 and d["language"] == "ru")
```

### Computing Statistics
```python
# User solved problems
submissions = load_json("submissions/submissions.json")
user_subs = [s for s in submissions if s["user_id"] == 1]
solved_problems = set(s["problem_id"] for s in user_subs)

# Best time for problem
problem_subs = [s for s in user_subs if s["problem_id"] == 1]
best_time = min(s["total_time_ms"] for s in problem_subs)
```

## File Size Expectations

| File | Records | Size (estimated) |
|------|---------|------------------|
| problems.json | 100-500 | 5-25 KB |
| problem_selectors.json | 100-500 | 20-100 KB |
| titles.json | 200-1000 | 10-50 KB |
| test_cases.json | 500-5000 | 50-500 KB |
| users.json | 1-10000 | 10-1000 KB |
| submissions.json | 100-100000 | 100KB-10MB |

**Note:** Submissions can grow large → migration to database important for production.

## Validation

Each JSON file should validate against its schema (future: JSON Schema definitions).

Current validation rules:
- **Foreign keys:** All references must exist
- **Enums:** Values must match defined enums
- **Unique constraints:** (user_id, problem_id, programming_language) for drafts
- **Required fields:** No nulls for required fields

## Contributing

When adding new problems:
1. Add to `problems.json` (new problem_id)
2. Add metadata to `problem_selectors.json`
3. Add titles for all supported languages
4. Add descriptions for all supported languages
5. Add examples with explanations
6. Add at least one hint
7. Add editorial
8. Add function signatures for all languages
9. Add at least one canonical solution
10. Add test cases (mark examples with `is_example: true`)
11. Add tags

See existing problems as examples.
