# miniRDB — 最小RDBMSのサンプル

これはRDBMSの基本概念を学ぶための最小実装サンプルです。

- サポートするSQL: `CREATE TABLE`, `INSERT`, `SELECT`（簡易WHEREの等価比較のみ）
- 型: `INT`, `TEXT`（簡易的に扱います）
- 永続化: テーブルごとに `data/{table}.schema.json` と `data/{table}.data` を作成し、append-onlyで行を保存します

使い方:

1. REPLを起動:

```bash
python -m minirdb.cli
```

2. `examples/commands.txt` を参考にSQLを実行してください。

このプロジェクトは教育目的に限定した非常に小さな実装です。本格的なRDBMSの機能（トランザクション、インデックス、最適化、複雑な型、エラーハンドリング等）は含みません。
