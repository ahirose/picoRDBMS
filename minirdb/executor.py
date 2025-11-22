from .storage import Storage
from .parser import parse_sql
from typing import Any, Dict, Optional, List


class Executor:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()

    def execute(self, ast: Dict[str, Any]):
        t = ast.get('type')
        if t == 'create':
            self.storage.create_table(ast['table'], ast['columns'])
            return {"status": "ok"}
        if t == 'insert':
            self.storage.insert(ast['table'], ast['row'])
            return {"status": "ok"}
        if t == 'select':
            cols = ast.get('columns')
            if cols == ['*']:
                cols = None
            where = ast.get('where')
            rows = self.storage.select(ast['table'], columns=cols, where=where)
            return {"status": "ok", "rows": rows}
        raise ValueError('unknown AST type')
