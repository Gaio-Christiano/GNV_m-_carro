import py_compile
from pathlib import Path
py_compile.compile(str(Path(__file__).with_name('main.py')), doraise=True)
print('OK: main.py passou no py_compile.')
