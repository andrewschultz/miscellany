#
# i7h.py
# called by i7h.bat

import re
import os
import sys
import i7

my_stuff = sys.argv[1:]

if my_stuff[1] in i7.i7x.keys() and my_stuff[0] in i7.i7hxf.keys():
	print("Going header-project instead of project-header")
	my_stuff.reverse()

hdr = re.sub("-", " ", i7.proj_exp(sys.argv[1]))

to_open = "{:s}\\{:s} {:s}.i7x".format(i7.extdir, hdr.title(), i7.th_exp(sys.argv[2]))

if os.path.exists(to_open):
	print("Opening", to_open)
    i7.npo(to_open)
else:
	print("No such path", to_open)