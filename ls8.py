"""Main."""

import sys
from cpu import *

if len(sys.argv) == 2:
    filename= sys.argv[1]
    cpu = CPU()
    cpu.load(filename)
    cpu.run()
else:
    print('Error: please provide a file name to execute instruction');
    sys.exit(1)
