# picoRDBMS

This repository contains educational samples and experiments for building a very small, minimal RDBMS implementation named `minirdb`.

**What I added**
- `minirdb/` — a tiny Python package implementing a minimal RDBMS:
  - `minirdb/storage.py`: append-only per-table storage and simple JSON schema files (`data/{table}.schema.json`, `data/{table}.data`).
  - `minirdb/parser.py`: minimal SQL parser for `CREATE TABLE`, `INSERT`, and `SELECT` (simple `WHERE` equality only).
  - `minirdb/executor.py`: executes parsed ASTs against the storage layer.
  - `minirdb/cli.py`: a small REPL to run SQL interactively (`python -m minirdb.cli`).
- `examples/commands.txt` — sample SQL commands for smoke testing.
- `MINIRDB_README.md` — short notes explaining the design and usage.

**Quick start**

1. Run the interactive REPL:

```bash
python -m minirdb.cli
```

2. Or run the example batch (creates a `test_run/` data directory):

```bash
python3 - <<'PY'
from minirdb.parser import parse_sql
from minirdb.executor import Executor
from minirdb.storage import Storage
import shutil, os
run_dir='test_run'
if os.path.exists(run_dir):
    shutil.rmtree(run_dir)
storage=Storage(run_dir)
execer=Executor(storage)
lines=[]
for ln in open('examples/commands.txt','r',encoding='utf-8'):
    s=ln.strip()
    if s.startswith('--') or not s:
        continue
    lines.append(s)
text='\n'.join(lines)
for part in text.split(';'):
    stmt=part.strip()
    if not stmt:
        continue
    ast=parse_sql(stmt+';')
    print('> ', stmt+';')
    res=execer.execute(ast)
    if 'rows' in res:
        for r in res['rows']:
            print(r)
    else:
        print(res)
PY
```

**Notes & next steps**
- This code is for learning only — it intentionally omits many real RDBMS features (transactions, indexes, query planning, concurrency, complex types).
- Consider adding a `.gitignore` to exclude `data/`, `test_run/`, `testdata/` and `__pycache__/` directories before committing more test artifacts.
- Suggested improvements: stronger type handling, WHERE expression parsing (AND/OR), basic indexing, and unit tests under `tests/`.

If you'd like, I can add a `.gitignore`, unit tests, or extend the parser/executor next.
