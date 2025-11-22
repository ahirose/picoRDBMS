from minirdb.executor import Executor
from minirdb.storage import Storage


def test_executor_flow(tmp_path):
    run_dir = str(tmp_path / "db")
    storage = Storage(run_dir)
    execer = Executor(storage)
    # create
    ast = {"type": "create", "table": "users", "columns": [("id", "INT"), ("name", "TEXT")]} 
    res = execer.execute(ast)
    assert res['status'] == 'ok'
    # insert
    res = execer.execute({"type": "insert", "table": "users", "row": {"id": 1, "name": "X"}})
    assert res['status'] == 'ok'
    # select
    res = execer.execute({"type": "select", "table": "users", "columns": ['*'], "where": None})
    assert res['status'] == 'ok'
    assert len(res['rows']) == 1
