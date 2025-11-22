import os
import json
from typing import List, Dict, Tuple, Optional, Any


class Storage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _schema_path(self, table: str) -> str:
        return os.path.join(self.data_dir, f"{table}.schema.json")

    def _data_path(self, table: str) -> str:
        return os.path.join(self.data_dir, f"{table}.data")

    def create_table(self, table: str, columns: List[Tuple[str, str]]):
        """Create a table with columns = [(name, type), ...]."""
        schema_path = self._schema_path(table)
        if os.path.exists(schema_path):
            raise FileExistsError(f"table '{table}' already exists")
        schema = {"columns": [{"name": n, "type": t} for n, t in columns]}
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f)
        # create empty data file
        open(self._data_path(table), "a", encoding="utf-8").close()

    def table_exists(self, table: str) -> bool:
        return os.path.exists(self._schema_path(table))

    def _load_schema(self, table: str) -> Dict[str, Any]:
        schema_path = self._schema_path(table)
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"no such table '{table}'")
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def insert(self, table: str, row: Dict[str, Any]):
        schema = self._load_schema(table)
        cols = [c["name"] for c in schema["columns"]]
        # simple type handling
        typed_row = {}
        for col in cols:
            if col not in row:
                typed_row[col] = None
            else:
                val = row[col]
                # find type
                ctype = next((c["type"] for c in schema["columns"] if c["name"] == col), "TEXT")
                if ctype.upper() == "INT":
                    try:
                        typed_row[col] = int(val)
                    except Exception:
                        raise ValueError(f"column '{col}' expects INT")
                else:
                    typed_row[col] = str(val)

        with open(self._data_path(table), "a", encoding="utf-8") as f:
            f.write(json.dumps(typed_row, ensure_ascii=False) + "\n")

    def select(self, table: str, columns: Optional[List[str]] = None, where: Optional[Tuple[str, Any]] = None):
        """Select rows. where: (col, value) for equality filter."""
        schema = self._load_schema(table)
        cols = [c["name"] for c in schema["columns"]]
        if columns is None:
            columns = cols

        result = []
        with open(self._data_path(table), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if where is not None:
                    col, val = where
                    if row.get(col) != val:
                        continue
                projected = {c: row.get(c) for c in columns}
                result.append(projected)
        return result
