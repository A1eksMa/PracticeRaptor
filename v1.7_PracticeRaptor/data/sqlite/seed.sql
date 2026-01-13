-- PracticeRaptor SQLite Seed Data
-- Same data as JSON files

-- ============================================================
-- PROBLEMS
-- ============================================================

INSERT INTO problems (problem_id, difficulty, complexity, categories, supported_languages) VALUES
(1, 'easy', 'O(n)', '["Array", "Hash Table"]', '["python3", "java"]'),
(2, 'easy', 'O(n)', '["String", "Two Pointers"]', '["python3"]');

-- ============================================================
-- TITLES
-- ============================================================

INSERT INTO titles (problem_id, language, title) VALUES
(1, 'en', 'Two Sum'),
(1, 'ru', 'Два числа'),
(2, 'en', 'Reverse String'),
(2, 'ru', 'Развернуть строку');

-- ============================================================
-- DESCRIPTIONS
-- ============================================================

INSERT INTO descriptions (problem_id, language, description) VALUES
(1, 'en', 'Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.'),
(1, 'ru', 'Дан массив целых чисел `nums` и целое число `target`. Верните индексы двух чисел, сумма которых равна `target`.

Можно предположить, что каждый вход имеет ровно одно решение, и нельзя использовать один и тот же элемент дважды.'),
(2, 'en', 'Write a function that reverses a string. The input string is given as an array of characters.'),
(2, 'ru', 'Напишите функцию, которая разворачивает строку. Входная строка задана как массив символов.');

-- ============================================================
-- EXAMPLES
-- ============================================================

INSERT INTO examples (example_id, problem_id, input, output) VALUES
(1, 1, 'nums = [2, 7, 11, 15], target = 9', '[0, 1]'),
(2, 1, 'nums = [3, 2, 4], target = 6', '[1, 2]'),
(3, 2, 's = ["h", "e", "l", "l", "o"]', '["o", "l", "l", "e", "h"]');

-- ============================================================
-- EXPLANATIONS
-- ============================================================

INSERT INTO explanations (example_id, language, explanation) VALUES
(1, 'en', 'Because nums[0] + nums[1] == 9, we return [0, 1].'),
(1, 'ru', 'Поскольку nums[0] + nums[1] == 9, возвращаем [0, 1].'),
(2, 'en', 'Because nums[1] + nums[2] == 6, we return [1, 2].'),
(2, 'ru', 'Поскольку nums[1] + nums[2] == 6, возвращаем [1, 2].');

-- ============================================================
-- HINTS
-- ============================================================

INSERT INTO hints (problem_id, language, hint_index, hint) VALUES
(1, 'en', 0, 'Try using a hash map to store values you''ve seen.'),
(1, 'ru', 0, 'Попробуйте использовать хеш-таблицу для хранения уже просмотренных значений.'),
(1, 'en', 1, 'For each number, check if target - number exists in the hash map.'),
(1, 'ru', 1, 'Для каждого числа проверьте, существует ли target - number в хеш-таблице.');

-- ============================================================
-- TAGS
-- ============================================================

INSERT INTO tags (problem_id, tag) VALUES
(1, 'array'),
(1, 'hash-table'),
(2, 'string'),
(2, 'two-pointers');

-- ============================================================
-- EDITORIALS
-- ============================================================

INSERT INTO editorials (problem_id, language, editorial) VALUES
(1, 'en', '## Approach 1: Hash Map

We can solve this problem in O(n) time using a hash map.

1. Iterate through the array
2. For each element, check if `target - element` exists in the hash map
3. If yes, return the indices
4. If no, add current element to the hash map'),
(1, 'ru', '## Подход 1: Хеш-таблица

Мы можем решить эту задачу за O(n) времени, используя хеш-таблицу.

1. Проходим по массиву
2. Для каждого элемента проверяем, есть ли `target - element` в хеш-таблице
3. Если да — возвращаем индексы
4. Если нет — добавляем текущий элемент в хеш-таблицу');

-- ============================================================
-- SIGNATURES
-- ============================================================

INSERT INTO signatures (problem_id, programming_language, template, function_name) VALUES
(1, 'python3', 'def two_sum(nums: list[int], target: int) -> list[int]:', 'two_sum'),
(1, 'java', 'public int[] twoSum(int[] nums, int target)', 'twoSum'),
(2, 'python3', 'def reverse_string(s: list[str]) -> None:', 'reverse_string');

-- ============================================================
-- TEST CASES
-- ============================================================

INSERT INTO test_cases (test_case_id, problem_id, programming_language, code, is_example) VALUES
(1, 1, 'python3', 'assert two_sum([2, 7, 11, 15], 9) == [0, 1]', 1),
(2, 1, 'python3', 'assert two_sum([3, 2, 4], 6) == [1, 2]', 1),
(3, 1, 'python3', 'assert two_sum([3, 3], 6) == [0, 1]', 0),
(4, 1, 'python3', 'assert two_sum([1, 2, 3, 4, 5], 9) == [3, 4]', 0),
(5, 2, 'python3', 's = [''h'', ''e'', ''l'', ''l'', ''o'']; reverse_string(s); assert s == [''o'', ''l'', ''l'', ''e'', ''h'']', 1);

-- ============================================================
-- CANONICAL SOLUTIONS
-- ============================================================

INSERT INTO canonical_solutions (canonical_solution_id, problem_id, programming_language, name, complexity, code) VALUES
(1, 1, 'python3', 'Hash Map (One Pass)', 'O(n)', 'def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []'),
(2, 1, 'python3', 'Brute Force', 'O(n²)', 'def two_sum(nums: list[int], target: int) -> list[int]:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []'),
(3, 2, 'python3', 'Two Pointers', 'O(n)', 'def reverse_string(s: list[str]) -> None:
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1');
