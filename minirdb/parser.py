import re
from typing import Dict, Any, List, Tuple, Optional


_CREATE_RE = re.compile(r"^CREATE\s+TABLE\s+(?P<table>\w+)\s*\((?P<cols>.+)\)\s*;?$", re.I)
_INSERT_RE = re.compile(r"^INSERT\s+INTO\s+(?P<table>\w+)\s*\((?P<cols>[^)]+)\)\s*VALUES\s*\((?P<vals>[^)]+)\)\s*;?$", re.I)
_SELECT_RE = re.compile(r"^SELECT\s+(?P<cols>[\w\*,\s]+)\s+FROM\s+(?P<table>\w+)(?:\s+WHERE\s+(?P<where>.+))?\s*;?$", re.I)


def _split_cols(s: str) -> List[str]:
    return [p.strip() for p in s.split(',') if p.strip()]


def parse_create(sql: str) -> Dict[str, Any]:
    m = _CREATE_RE.match(sql.strip())
    if not m:
        raise ValueError("invalid CREATE statement")
    table = m.group('table')
    cols_raw = m.group('cols')
    parts = _split_cols(cols_raw)
    cols = []
    for p in parts:
        toks = p.split()
        if len(toks) < 2:
            raise ValueError(f"invalid column definition: {p}")
        name = toks[0]
        ctype = toks[1]
        cols.append((name, ctype.upper()))
    return {"type": "create", "table": table, "columns": cols}


def parse_insert(sql: str) -> Dict[str, Any]:
    m = _INSERT_RE.match(sql.strip())
    if not m:
        raise ValueError("invalid INSERT statement")
    table = m.group('table')
    cols = _split_cols(m.group('cols'))
    vals = _split_cols(m.group('vals'))
    # strip quotes from vals
    parsed_vals = []
    for v in vals:
        v = v.strip()
        if v.startswith("'") and v.endswith("'"):
            parsed_vals.append(v[1:-1])
        elif v.isdigit() or (v.startswith('-') and v[1:].isdigit()):
            parsed_vals.append(int(v))
        else:
            # treat as bareword string
            parsed_vals.append(v)
    if len(cols) != len(parsed_vals):
        raise ValueError("columns/values length mismatch")
    row = dict(zip(cols, parsed_vals))
    return {"type": "insert", "table": table, "row": row}


def parse_select(sql: str) -> Dict[str, Any]:
    m = _SELECT_RE.match(sql.strip())
    if not m:
        raise ValueError("invalid SELECT statement")
    cols_raw = m.group('cols')
    table = m.group('table')
    where_raw = m.group('where')
    cols = [c.strip() for c in cols_raw.split(',')] if cols_raw.strip() != '*' else ['*']
    where = None
    if where_raw:
        # only support simple equality: col = value
        parts = where_raw.split('=', 1)
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            # remove possible trailing semicolon or whitespace
            right = right.rstrip().rstrip(';').strip()
            # handle quoted string
            if right.startswith("'") and right.endswith("'") and len(right) >= 2:
                right = right[1:-1]
            elif right.isdigit() or (right.startswith('-') and right[1:].isdigit()):
                right = int(right)
            where = (left, right)
        else:
            raise ValueError("only simple equality WHERE supported")
    return {"type": "select", "table": table, "columns": cols, "where": where}


def parse_sql(sql: str) -> Dict[str, Any]:
    s = sql.strip()
    if s.upper().startswith('CREATE'):
        return parse_create(sql)
    if s.upper().startswith('INSERT'):
        return parse_insert(sql)
    if s.upper().startswith('SELECT'):
        return parse_select(sql)
    raise ValueError('unsupported SQL')
