# ni.py
# python based replacement (of sorts) for batch files ni.bat and gh.bat
# they will be renamed niold.bat and ghold.bat

import sys
import mytools as mt

def usage(header="Generic usage writeup"):
    mt.okay(header)
    print("This is a quasi-replacement for the batch file ni.bat.")
    print()
    mt.warn("Examples of usage:")
    print("ni t opens the source file in the current directory.")
    print("ni vf ta opens up VVFF's tables.")
    sys.exit()

cmd_count = 1

if len(sys.argv) == 1:
    usage("No commands given")

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg == '?':
        usage("USAGE")
    else:
        usage("Bad parameter {}.".format(arg))
    cmd_count += 1
