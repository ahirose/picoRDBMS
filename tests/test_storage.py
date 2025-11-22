import shutil
import os
from minirdb.storage import Storage


def test_create_insert_select(tmp_path):
    run_dir = str(tmp_path / "db")
    s = Storage(run_dir)
    s.create_table('t', [('id', 'INT'), ('name', 'TEXT')])
    s.insert('t', {'id': 1, 'name': 'A'})
    s.insert('t', {'id': 2, 'name': 'B'})
    rows = s.select('t')
    assert len(rows) == 2
    assert rows[0]['id'] == 1
    assert rows[1]['name'] == 'B'
