---
name: python-production
description: Python production code patterns and anti-patterns. Use when writing Python code.
user-invocable: false
---

# Python Production Patterns

## Configuration: Dataclasses Over Dicts

- Use `@dataclass` with type annotations for structured config. Dicts hide bugs.
  ```python
  # BAD
  config = {"host": "localhost", "port": 8080}

  # GOOD
  @dataclass
  class ServerConfig:
      host: str
      port: int = 8080
  ```
- Use `@dataclass(frozen=True)` for immutable configuration
- For optional fields, use `Optional[T] = None`, not sentinel values

## Path Operations

- **Always use `pathlib.Path`**, never string concatenation:
  ```python
  # BAD
  path = base_dir + "/" + subdir + "/" + filename

  # GOOD
  path = Path(base_dir) / subdir / filename
  ```
- Use `.resolve()` to get absolute paths, `.exists()` to check, `.mkdir(parents=True, exist_ok=True)` to create

## Logging

- **One logger per module**: `logger = logging.getLogger(__name__)`
- **Configure logging at entry points only** (main, CLI, app startup). Never call `basicConfig()` or add handlers in library code.
- Use appropriate levels: `debug` for diagnostics, `info` for operational events, `warning` for recoverable issues, `error` for failures
- Use lazy formatting: `logger.info("Processing %s", filename)` not `logger.info(f"Processing {filename}")`

## Resource Management

- **Always use context managers** for resources:
  ```python
  # Files
  with open(path) as f:
      data = f.read()

  # Database connections
  with db.connect() as conn:
      conn.execute(query)

  # Locks
  with threading.Lock():
      shared_state.update(value)
  ```

## Mutable Default Arguments

- **Never use mutable defaults** — they persist across calls:
  ```python
  # BUG
  def add_item(item, items=[]):
      items.append(item)
      return items

  # CORRECT
  def add_item(item, items=None):
      if items is None:
          items = []
      items.append(item)
      return items
  ```

## Module API Surface

- Use `__all__` in `__init__.py` to control public exports:
  ```python
  __all__ = ["Analyzer", "run_analysis", "AnalysisConfig"]
  ```
- Only re-export what downstream users actually need
- Keep `__init__.py` minimal — imports and `__all__`, no logic

## Import Patterns

- **Lazy imports only when measured startup time justifies it.** Don't guess — profile first.
- Standard import order: stdlib, third-party, local (blank line between groups)
- No wildcard imports (`from module import *`)

## Subprocess Calls

- Always use `subprocess.run()` with explicit args list:
  ```python
  # BAD
  subprocess.run(f"cmd {user_input}", shell=True)

  # GOOD
  result = subprocess.run(
      ["cmd", user_input],
      capture_output=True,
      text=True,
      check=True,
  )
  ```
- Use `check=True` to raise on non-zero exit codes (or handle returncode explicitly)

## Exception Handling

- **Define a project-level base exception**, inherit specific exceptions from it:
  ```python
  class AppError(Exception):
      """Base exception for this project."""

  class ConfigError(AppError):
      """Invalid configuration."""

  class DataLoadError(AppError):
      """Failed to load data from source."""
  ```
- **Never bare `except:`** — always catch specific exceptions
- **Don't silence exceptions** without logging:
  ```python
  # BAD
  try:
      process(data)
  except Exception:
      pass

  # ACCEPTABLE (when you genuinely expect and handle the case)
  try:
      value = cache[key]
  except KeyError:
      value = compute_value(key)
  ```

## Design Principles

- **Composition over inheritance**: inject dependencies, don't subclass for code reuse
- **Functions over classes for stateless operations**: if your class has no `__init__` state and one method, it should be a function
- **Use `enum.Enum` for fixed sets**, not string constants:
  ```python
  # BAD
  mode = "read"  # typo-prone, no IDE completion

  # GOOD
  class Mode(enum.Enum):
      READ = "read"
      WRITE = "write"
  ```

## String Formatting

- **f-strings** for simple interpolation: `f"Hello, {name}"`
- **`.format()`** only when the template is stored separately
- Never use `%` formatting in new code

## Type Annotations

- **Required on public API signatures** (functions, methods, class attributes exposed in `__all__`)
- Don't over-annotate private helpers — type checkers can infer most local types
- Use `from __future__ import annotations` for forward references (Python 3.9 compatibility)
- Common patterns:
  ```python
  def load_config(path: Path) -> ServerConfig: ...
  def find_items(query: str, limit: int = 10) -> list[Item]: ...
  def process(data: dict[str, Any]) -> None: ...
  ```

## Module Entry Points

- Always use the `__main__` guard in executable modules:
  ```python
  def main():
      # entry point logic

  if __name__ == "__main__":
      main()
  ```
- This prevents side effects when the module is imported for testing
