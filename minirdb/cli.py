import sys
from .parser import parse_sql
from .executor import Executor


def repl():
    execer = Executor()
    print("minirdb REPL — supported: CREATE, INSERT, SELECT. Type 'quit' to exit.")
    buf = ''
    try:
        while True:
            try:
                if buf:
                    prompt = '... '
                else:
                    prompt = 'minirdb> '
                line = input(prompt)
            except EOFError:
                print()
                break
            if not line:
                continue
            if line.strip().lower() in ('quit', 'exit'):
                break
            buf += ' ' + line
            if ';' not in line:
                continue
            statement, rest = buf.split(';', 1)
            buf = rest.strip()
            try:
                ast = parse_sql(statement + ';')
                res = execer.execute(ast)
                if 'rows' in res:
                    for r in res['rows']:
                        print(r)
                else:
                    print(res)
            except Exception as e:
                print('Error:', e)
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    repl()
