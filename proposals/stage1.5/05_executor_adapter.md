# Step 5: Executor Adapter (Local)

## Цель

Рефакторинг текущего executor в адаптер, совместимый с ICodeExecutor Protocol.

## Задачи

### 5.1. Создать LocalExecutor

```python
# adapters/executors/local_executor.py
"""Local code executor using multiprocessing."""
import ast
import multiprocessing
import traceback
from copy import deepcopy
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from core.domain.models import TestCase, TestResult, ExecutionResult
from core.domain.result import Ok, Err, Result
from core.domain.errors import ExecutionError
from core.ports.executors import ICodeExecutor


@dataclass(frozen=True)
class ExecutorConfig:
    """Configuration for local executor."""
    timeout_sec: int = 5
    memory_limit_mb: int = 256


# Safe builtins whitelist
SAFE_BUILTINS = {
    # Types
    'bool', 'int', 'float', 'complex', 'str', 'bytes', 'bytearray',
    'list', 'tuple', 'set', 'frozenset', 'dict',
    'type', 'object', 'slice', 'range',
    # Functions
    'abs', 'all', 'any', 'bin', 'chr', 'divmod', 'enumerate',
    'filter', 'format', 'hash', 'hex', 'id', 'isinstance', 'issubclass',
    'iter', 'len', 'map', 'max', 'min', 'next', 'oct', 'ord', 'pow',
    'print', 'repr', 'reversed', 'round', 'sorted', 'sum', 'zip',
    # Exceptions
    'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
    'AttributeError', 'RuntimeError', 'StopIteration', 'ZeroDivisionError',
    # Constants
    'True', 'False', 'None',
}


def _create_sandbox_globals() -> dict:
    """Create restricted globals for code execution."""
    safe_builtins = {
        name: getattr(__builtins__ if isinstance(__builtins__, dict)
                      else __builtins__.__dict__, name, None)
        for name in SAFE_BUILTINS
    }
    safe_builtins['__builtins__'] = safe_builtins
    return safe_builtins


def _execute_in_process(
    code: str,
    test_case_data: dict,
    function_name: str,
    result_queue: multiprocessing.Queue,
) -> None:
    """Execute code in separate process (for isolation)."""
    try:
        sandbox = _create_sandbox_globals()

        # Execute user code
        exec(code, sandbox)

        if function_name not in sandbox:
            result_queue.put({
                'success': False,
                'error': f"Function '{function_name}' not found in code",
                'error_type': 'runtime',
            })
            return

        func = sandbox[function_name]

        # Deep copy inputs to prevent mutation
        inputs = deepcopy(test_case_data['input'])

        # Execute function
        start_time = perf_counter()
        actual = func(**inputs)
        execution_time_ms = int((perf_counter() - start_time) * 1000)

        result_queue.put({
            'success': True,
            'actual': actual,
            'execution_time_ms': execution_time_ms,
        })

    except SyntaxError as e:
        result_queue.put({
            'success': False,
            'error': f"Syntax error: {e}",
            'error_type': 'syntax',
        })
    except Exception as e:
        result_queue.put({
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'error_type': 'runtime',
        })


class LocalExecutor:
    """Local code executor using multiprocessing for isolation."""

    def __init__(self, config: ExecutorConfig | None = None):
        self.config = config or ExecutorConfig()

    def validate_syntax(self, code: str) -> Result[None, ExecutionError]:
        """Check if code has valid Python syntax."""
        try:
            ast.parse(code)
            return Ok(None)
        except SyntaxError as e:
            return Err(ExecutionError(
                message=f"Line {e.lineno}: {e.msg}",
                error_type="syntax",
            ))

    def execute(
        self,
        code: str,
        test_cases: tuple[TestCase, ...],
        function_name: str,
        timeout_sec: int | None = None,
    ) -> Result[ExecutionResult, ExecutionError]:
        """Execute code against test cases."""

        # Validate syntax first
        syntax_result = self.validate_syntax(code)
        if syntax_result.is_err():
            return Err(syntax_result.error)

        timeout = timeout_sec or self.config.timeout_sec
        test_results: list[TestResult] = []
        total_time_ms = 0
        all_passed = True

        for test_case in test_cases:
            result = self._run_single_test(code, test_case, function_name, timeout)

            match result:
                case Ok(test_result):
                    test_results.append(test_result)
                    total_time_ms += test_result.execution_time_ms
                    if not test_result.passed:
                        all_passed = False
                        break  # Stop on first failure
                case Err(error):
                    return Err(error)

        return Ok(ExecutionResult(
            success=all_passed,
            test_results=tuple(test_results),
            total_time_ms=total_time_ms,
        ))

    def _run_single_test(
        self,
        code: str,
        test_case: TestCase,
        function_name: str,
        timeout_sec: int,
    ) -> Result[TestResult, ExecutionError]:
        """Run a single test case."""

        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_execute_in_process,
            args=(code, {'input': test_case.input}, function_name, result_queue),
        )

        process.start()
        process.join(timeout=timeout_sec)

        if process.is_alive():
            process.terminate()
            process.join()
            return Ok(TestResult(
                test_case=test_case,
                passed=False,
                error_message=f"Timeout: exceeded {timeout_sec}s",
            ))

        if result_queue.empty():
            return Err(ExecutionError(
                message="Process terminated unexpectedly",
                error_type="runtime",
            ))

        result_data = result_queue.get()

        if not result_data['success']:
            return Ok(TestResult(
                test_case=test_case,
                passed=False,
                error_message=result_data['error'],
            ))

        actual = result_data['actual']
        passed = self._compare_results(actual, test_case.expected)

        return Ok(TestResult(
            test_case=test_case,
            passed=passed,
            actual=actual,
            execution_time_ms=result_data['execution_time_ms'],
            error_message=None if passed else f"Expected {test_case.expected}, got {actual}",
        ))

    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual and expected results."""
        # Handle float comparison with tolerance
        if isinstance(actual, float) and isinstance(expected, float):
            return abs(actual - expected) < 1e-9

        # Handle list/tuple comparison
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            if len(actual) != len(expected):
                return False
            return all(
                self._compare_results(a, e)
                for a, e in zip(actual, expected)
            )

        # Direct comparison
        return actual == expected
```

### 5.2. Обновить adapters/executors/__init__.py

```python
# adapters/executors/__init__.py
"""Executor adapters."""
from .local_executor import LocalExecutor, ExecutorConfig

__all__ = [
    "LocalExecutor",
    "ExecutorConfig",
]
```

## Сравнение с текущим кодом

| Аспект | Текущий prototype/executor.py | Новый LocalExecutor |
|--------|------------------------------|---------------------|
| Интерфейс | Функции | Protocol-compatible class |
| Результат | dict/exceptions | Result[ExecutionResult, Error] |
| Конфигурация | Константы | ExecutorConfig dataclass |
| Тестируемость | Сложно | Легко (DI) |

## Критерии готовности

- [ ] LocalExecutor реализует ICodeExecutor Protocol
- [ ] validate_syntax возвращает Result
- [ ] execute возвращает Result[ExecutionResult, ExecutionError]
- [ ] Timeout работает через multiprocessing
- [ ] Sandbox ограничивает builtins
- [ ] Тесты покрывают все сценарии

## Тесты для Step 5

```python
# tests/unit/adapters/executors/test_local_executor.py
import pytest
from adapters.executors.local_executor import LocalExecutor, ExecutorConfig
from core.domain.models import TestCase


@pytest.fixture
def executor():
    return LocalExecutor(ExecutorConfig(timeout_sec=2))


@pytest.fixture
def simple_test_case():
    return TestCase(
        input={"x": 5},
        expected=10,
    )


class TestValidateSyntax:
    def test_valid_code_returns_ok(self, executor):
        code = "def solution(x): return x * 2"
        result = executor.validate_syntax(code)
        assert result.is_ok()

    def test_invalid_code_returns_error(self, executor):
        code = "def solution(x) return x"  # Missing colon
        result = executor.validate_syntax(code)
        assert result.is_err()
        assert "syntax" in result.error.error_type.lower()


class TestExecute:
    def test_correct_solution_passes(self, executor, simple_test_case):
        code = "def solution(x): return x * 2"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is True
        assert exec_result.passed_count == 1

    def test_wrong_answer_fails(self, executor, simple_test_case):
        code = "def solution(x): return x + 1"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert exec_result.test_results[0].passed is False

    def test_timeout_is_handled(self, executor, simple_test_case):
        code = """
def solution(x):
    while True:
        pass
    return x
"""
        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
            timeout_sec=1,
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert "timeout" in exec_result.test_results[0].error_message.lower()

    def test_runtime_error_is_captured(self, executor, simple_test_case):
        code = "def solution(x): return 1 / 0"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert "ZeroDivision" in exec_result.test_results[0].error_message

    def test_missing_function_is_error(self, executor, simple_test_case):
        code = "def other_func(x): return x"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
```

## Следующий шаг

После завершения Step 5 переходите к [Step 6: Core Services](./06_core_services.md).
