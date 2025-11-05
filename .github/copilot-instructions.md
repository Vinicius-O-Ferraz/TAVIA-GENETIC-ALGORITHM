## Quick context

This repository implements a small genetic-algorithm-based timetable/scheduling model in Python. The runnable code is in the `code/` directory and contains minimal, self-contained model classes used to represent solutions, periods, classes (turmas) and professors.

Key files to inspect for behaviour and examples:
- `code/Solucao.py` — `solucao` holds a list of `periodo` objects (default 8 periods).
- `code/Periodo.py` — `periodo` stores a 2×5 `matriz` (list of lists) used for schedule slots.
- `code/Turma.py` — `turma` records `id_turma`, `professor`, `horarios`, `semestre_letivo`, `carga_horaria`.
- `code/Professores.py` — expected mapping of professor -> list of subject codes (note: current file has syntax issues; see "Common fixes" below).

## Big-picture architecture & data flow (short)

- Representation: a `solucao` contains a list of `periodo` objects. Each `periodo` contains a `matriz` (2 rows × 5 columns) representing scheduling slots.
- Domain objects are lightweight, mutable Python classes (no dataclasses or type hints currently). Files are small and intended to be imported and manipulated from small scripts or an interactive session.
- Import pattern: modules use plain module-level imports (e.g. `from Periodo import periodo`) which assumes you run Python with the working directory set to `code/` (see Run/Debug guidance).

## Project-specific conventions you must follow

- Files live in `code/` and imports expect the process CWD to be `code/` (or PYTHONPATH adjusted). Prefer running scripts from inside `code/` to match current imports.
- Class names are written in lowercase (`solucao`, `periodo`, `turma`) — keep consistency when adding new model classes or tests.
- The repo currently uses plain lists/dicts for data and no external dependencies; keep changes minimal and self-contained unless you add a top-level packaging change (e.g., add `__init__.py`).

## Run, debug and quick checks (PowerShell)

Open a PowerShell terminal and run from the `code` folder to match import style:

```powershell
cd .\code
# Quick interactive check
python -c 'from Solucao import solucao; print(solucao(1))'

# Or start REPL and import
python
>>> from Solucao import solucao
>>> s = solucao(1)
>>> print(s)
```

Notes:
- If you prefer running from the repository root, add `code` to `PYTHONPATH` or convert `code/` into a package (add `__init__.py`) and update imports to a package style.

## Common fixes and gotchas (concrete examples)

- Professores.py currently contains a non-valid literal mapping like:

```py
professores = [
    "Taciana Pontal": ["PCO"],
    "Rodrigo Rosal": ["FED"],
]
```

This is invalid Python. Use a dictionary instead (and keep the file encoding/quotes consistent):

```py
professores = {
    "Taciana Pontal": ["PCO"],
    "Rodrigo Rosal": ["FED"],
}
```

- Keep class and attribute names consistent: `solucao.periodos` is a list of `periodo` instances, and `periodo.matriz` is a list of lists of ints. Use these fields directly when implementing fitness, crossover, or mutation operations.

## Where to change things when extending

- Add new GA operators (fitness/crossover/mutation) in a new file under `code/` (e.g. `code/ga_ops.py`). Keep imports local (run from `code/`) or convert `code/` into a package before changing import style.
- If you add tests, create a `tests/` folder at repo root and use `pytest`. When running tests, ensure `PYTHONPATH=./code` or add `conftest.py` that inserts `code/` on sys.path.

## Examples of common tasks for an AI assistant

- "Implement a fitness function that penalizes professor conflicts": look at `turma.professor` and `solucao.periodos[*].matriz` to compute collisions.
- "Add a crossover that swaps periods": operate on `solucao.periodos` (a list) and swap slices between two solutions.
- "Fix Professores.py to be valid and export a helper function to list professors": convert the data to a dict and add a small accessor.

## Minimal checklist before opening a PR

- Run the simple interactive check from `code/` (see commands above).
- Keep the import pattern consistent (or convert the whole folder to a package in a single PR).
- Add a short unit test for any behavioural change (example: create two `solucao` instances and assert period length is 8).

---

If anything in this file is unclear or you want me to emphasize a different area (tests, packaging, or adding a runnable CLI), tell me which area and I will update this guidance. 
