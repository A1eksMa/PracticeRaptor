-- PracticeRaptor SQLite Schema
-- Mirrors JSON structure exactly: one JSON file = one table

-- ============================================================
-- PROBLEM TABLES
-- ============================================================

CREATE TABLE problems (
    problem_id INTEGER PRIMARY KEY,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    complexity TEXT NOT NULL,
    categories TEXT NOT NULL,  -- JSON array: ["Array", "Hash Table"]
    supported_languages TEXT NOT NULL  -- JSON array: ["python3", "java"]
);

CREATE TABLE titles (
    problem_id INTEGER NOT NULL,
    language TEXT NOT NULL CHECK (language IN ('en', 'ru')),
    title TEXT NOT NULL,
    PRIMARY KEY (problem_id, language),
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE descriptions (
    problem_id INTEGER NOT NULL,
    language TEXT NOT NULL CHECK (language IN ('en', 'ru')),
    description TEXT NOT NULL,
    PRIMARY KEY (problem_id, language),
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE examples (
    example_id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE explanations (
    example_id INTEGER NOT NULL,
    language TEXT NOT NULL CHECK (language IN ('en', 'ru')),
    explanation TEXT NOT NULL,
    PRIMARY KEY (example_id, language),
    FOREIGN KEY (example_id) REFERENCES examples(example_id)
);

CREATE TABLE hints (
    problem_id INTEGER NOT NULL,
    language TEXT NOT NULL CHECK (language IN ('en', 'ru')),
    hint_index INTEGER NOT NULL,
    hint TEXT NOT NULL,
    PRIMARY KEY (problem_id, language, hint_index),
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE tags (
    problem_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (problem_id, tag),
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE editorials (
    problem_id INTEGER NOT NULL,
    language TEXT NOT NULL CHECK (language IN ('en', 'ru')),
    editorial TEXT NOT NULL,
    PRIMARY KEY (problem_id, language),
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

-- ============================================================
-- SOLUTION TABLES
-- ============================================================

CREATE TABLE signatures (
    problem_id INTEGER NOT NULL,
    programming_language TEXT NOT NULL CHECK (programming_language IN ('python3', 'java')),
    template TEXT NOT NULL,
    function_name TEXT NOT NULL,
    PRIMARY KEY (problem_id, programming_language),
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE test_cases (
    test_case_id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    programming_language TEXT NOT NULL CHECK (programming_language IN ('python3', 'java')),
    code TEXT NOT NULL,
    is_example INTEGER NOT NULL DEFAULT 0,  -- SQLite: 0=false, 1=true
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE canonical_solutions (
    canonical_solution_id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    programming_language TEXT NOT NULL CHECK (programming_language IN ('python3', 'java')),
    name TEXT NOT NULL,
    complexity TEXT NOT NULL,
    code TEXT NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Fast lookup by problem
CREATE INDEX idx_titles_problem ON titles(problem_id);
CREATE INDEX idx_descriptions_problem ON descriptions(problem_id);
CREATE INDEX idx_examples_problem ON examples(problem_id);
CREATE INDEX idx_hints_problem ON hints(problem_id);
CREATE INDEX idx_tags_problem ON tags(problem_id);
CREATE INDEX idx_signatures_problem ON signatures(problem_id);
CREATE INDEX idx_test_cases_problem ON test_cases(problem_id);
CREATE INDEX idx_canonical_solutions_problem ON canonical_solutions(problem_id);

-- Fast filtering
CREATE INDEX idx_problems_difficulty ON problems(difficulty);
CREATE INDEX idx_tags_tag ON tags(tag);
