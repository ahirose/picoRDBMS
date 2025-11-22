# minimalRDBMS

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

---

日本語概要

このリポジトリは教育目的で作成した非常に小さなRDBMSのサンプル実装 `minirdb` を含みます。主な内容は次の通りです。

- `minirdb/storage.py`: テーブルごとにJSONスキーマ（`data/{table}.schema.json`）とappend-onlyのデータファイル（`data/{table}.data`）を使った簡易ストレージ。
- `minirdb/parser.py`: `CREATE TABLE`、`INSERT`、`SELECT`（簡易的な `WHERE` の等価比較のみ）を扱う最小限のSQLパーサ。
- `minirdb/executor.py`: パーサのASTをストレージに対して実行する簡易実行器。
- `minirdb/cli.py`: 対話的にSQLを実行できるREPL。

クイックスタート（日本語）:

1. REPL起動:

```bash
python -m minirdb.cli
```

2. 付属のサンプル `examples/commands.txt` を参考に、一括実行のスクリプトを使って動作確認できます（`test_run/` ディレクトリが作成されます）。

注記:
- 教育目的の簡易実装であり、トランザクション、インデックス、同時実行制御、複雑な型などは実装されていません。
- `data/` やテスト用の `test_run/`、`__pycache__/` 等は `.gitignore` に追加済みです。

必要であれば、次の作業（型処理の改善、WHERE式の拡張、簡易インデックス追加、CI導入など）を実装します。

---

## コードの読み方ガイド

このセクションでは、minirdb のコードを理解するための読み方と推奨順序を説明します。

### ファイル構成と役割

```
minirdb/
├── __init__.py   # パッケージ公開インターフェース
├── storage.py    # 永続化レイヤー（ファイルI/O、型チェック）
├── parser.py     # SQLパーサー（文字列→AST変換）
├── executor.py   # クエリ実行エンジン（AST→操作実行）
└── cli.py        # 対話型REPL（ユーザーインターフェース）
```

### アーキテクチャと依存関係

```
┌─────────────┐
│   cli.py    │  ← ユーザー入力を受け付け
└──────┬──────┘
       │
  ┌────┴────┐
  ▼         ▼
┌──────┐  ┌───────────┐
│parser│  │executor.py│ ← パーサー出力を実行
│.py   │  └─────┬─────┘
└──────┘        │
                ▼
          ┌───────────┐
          │storage.py │ ← ファイルシステム操作
          └───────────┘
```

### SQL処理の流れ

```
ユーザー入力: "SELECT id FROM users WHERE id = 1;"
       │
       ▼
┌──────────────────────────────────────┐
│ 1. cli.py: 入力受付・バッファリング   │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ 2. parser.py: SQL → AST辞書に変換    │
│    {                                  │
│      "type": "select",               │
│      "table": "users",               │
│      "columns": ["id"],              │
│      "where": ("id", 1)              │
│    }                                  │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ 3. executor.py: ASTのtypeで分岐      │
│    type='select' → storage.select() │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ 4. storage.py: ファイル読み込み・     │
│    WHERE条件フィルタ・結果返却        │
└──────────────────────────────────────┘
```

### 推奨するコード読解順序

RDBMSの動作原理を理解するため、**低レイヤーから高レイヤーへ**読み進めることを推奨します。

#### 第1段階: storage.py（永続化レイヤー）

**最初に読むべきファイル**です。RDBMSの最も基本的な機能を理解できます。

- `Storage` クラスの構造
- `create_table()`: スキーマJSONファイルの作成
- `insert()`: append-onlyでのデータ追記、型チェック
- `select()`: データファイルの読み込み、WHERE条件フィルタ

```python
# データの保存形式
data/{table}.schema.json  # 列名と型の定義
data/{table}.data         # 1行1JSONの形式でデータ保存
```

#### 第2段階: parser.py（SQL解析）

SQL文字列がどのように構造化データに変換されるかを学びます。

- `parse_sql()`: エントリーポイント、SQL種別の判定
- `parse_create()`: CREATE TABLE文の解析
- `parse_insert()`: INSERT文の解析
- `parse_select()`: SELECT文の解析、WHERE句の処理
- `_infer_type()`: リテラル値の型推定（INT/TEXT）

#### 第3段階: executor.py（実行エンジン）

パーサーとストレージを繋ぐ統合層です。最も短いファイルです。

- `Executor` クラス: Storage インスタンスを保持
- `execute()`: AST の `type` フィールドで処理を分岐
  - `'create'` → `storage.create_table()`
  - `'insert'` → `storage.insert()`
  - `'select'` → `storage.select()`

#### 第4段階: cli.py（REPL）

ユーザーインターフェースの実装を確認します。

- `repl()`: 対話ループ
- 複数行SQL入力のバッファリング（`;` で文の終端を判定）
- エラーハンドリングと結果表示

#### 第5段階: __init__.py（公開インターフェース）

パッケージとしての構成を確認します。

```python
from minirdb import Storage, parse_sql, Executor
```

### テストコードの読み方

各モジュールの動作確認には対応するテストファイルが役立ちます。

| 実装ファイル | テストファイル |
|-------------|---------------|
| storage.py  | tests/test_storage.py |
| parser.py   | tests/test_parser.py |
| executor.py | tests/test_executor.py |

テストを実行して動作を確認:

```bash
python -m pytest tests/
```

### 実際に動かしながら読む

1. REPLを起動して動作を確認しながら読む:
   ```bash
   python -m minirdb.cli
   ```

2. サンプルSQLを実行:
   ```sql
   CREATE TABLE users (id INT, name TEXT);
   INSERT INTO users (id, name) VALUES (1, 'Alice');
   SELECT id, name FROM users WHERE id = 1;
   ```

3. 各ステップでprintデバッグを追加して、データの流れを追跡する
