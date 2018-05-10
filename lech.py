# lech.py
#
# line ending check.py
#
# couldn't resist the silly acronym
#

import i7
import ctypes
import sys

if len(sys.argv) == 1:
	proj = i7.lpro('ai')
else:
	proj = i7.lpro(sys.argv[1])

q = i7.i7f[proj]

q.append(i7.src(proj))

oops = ""

# sample for quick check to fail
# q = ['zr.txt']
# print(q)

for x in q:
    f = open(x, "rb")
    r = f.readline()
    if r[-2:] == b'\r\n':
        oops += '-- ' + x + "\n"
    f.close()

if oops:
    messageBox2 = ctypes.windll.user32.MessageBoxA
    messageBox2(None, ('Check what programs recently run on:\n' + oops).encode('ascii'), 'Oops! Windows line ending!'.encode('ascii'), 0x0)
else:
    print("All files in project", proj, "passed with unix line endings!")