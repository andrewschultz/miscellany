import os
import sys
import i7
from mytools import nohy
from pathlib import Path
import subprocess

to_add = []

def usage():
	print("Use a project name as an argument.")
	exit()

cmd_count = 1

while cmd_count < len(sys.argv):
	arg = nohy(sys.argv[cmd_count])
	if arg in i7.i7x:
		to_add.append(arg)
	else:
		usage()
	cmd_count += 1

if len(to_add) == 0:
	to_add = [ 'ai' ]

for x in to_add:
	tf = i7.triz(x)
	print(x, tf)
	if not os.path.exists(tf):
		print("Uh oh. {0} is not a valid path for {1}.".format(tf, x))
		continue
	if os.path.islink(tf):
		print("Got symlink.")
		u = os.readlink(tf)
		x = Path(tf).resolve()
		if u == tf:
			sys.exit("Looping symlink {0}, bailing.".format(tf))
		print("Opening symlink", tf, "to", u)
		subprocess.Popen(["c:/tech/trizbort/trizbort.exe", u], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	else:
		print("Launching file", tf)
		subprocess.Popen(["c:/tech/trizbort/trizbort.exe", tf])