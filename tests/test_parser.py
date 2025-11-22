from minirdb.parser import parse_create, parse_insert, parse_select


def test_parse_create():
    ast = parse_create("CREATE TABLE users (id INT, name TEXT);")
    assert ast['type'] == 'create'
    assert ast['table'] == 'users'
    assert ('id', 'INT') in ast['columns']


def test_parse_insert():
    ast = parse_insert("INSERT INTO users (id, name) VALUES (1, 'Alice');")
    assert ast['type'] == 'insert'
    assert ast['row']['id'] == 1
    assert ast['row']['name'] == 'Alice'


def test_parse_select():
    ast = parse_select("SELECT id, name FROM users WHERE name = 'Alice';")
    assert ast['type'] == 'select'
    assert ast['where'] == ('name', 'Alice')
