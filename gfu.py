# gfu.py : git commit in the future (12:01 AM the next day)

import i7
import os
import sys

#schtasks /create /f /tn "Test" /tr "\"c:\program files\test.bat\" arg1 'arg 2 with spaces' arg3" /sc Daily /st 00:00

try:
	my_files = sys.argv[1]
	my_msg = sys.argv[2]
except:
	sys.exit("You need 2 arguments for a future commit: files to add, then commit message")

my_proj = i7.dir2proj(empty_if_unmatched = False)
if not my_proj:
	sys.exit("To run gfu, you need a valid project directory, preferably on github.")

add_task = "\"future-add-{}\"".format(my_proj)
commit_task = "\"future-commit-{}\"".format(my_proj)

os.system("schtasks /create /f /tn {} /tr \"git add {}\" /sc Once /st 00:01".format(add_task, my_files))
os.system("schtasks /create /f /tn {} /tr \"git commit -m \\\"{}\\\"\" /sc Once /st 00:01".format(commit_task, my_msg))