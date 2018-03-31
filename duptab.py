# duptab.py
#
# searches for duplicate-ish table entries
#

from collections import defaultdict
import re

dup_yet = defaultdict(int)
t2d = defaultdict(int)

table_file = 'c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\Ailihphilia Tables.i7x'

dupes = 0
in_table = False
line_num = 0
cur_table = "(none)"

with open(table_file) as file:
	for line in file:
		line_num = line_num + 1
		if line.startswith('table'):
			in_table = True
			cur_table = line.lower().strip()
			continue
		if not line.strip():
			in_table = False
			continue
		if in_table:
			ll = line.lower().strip().split("\t")
			if not ll[0].startswith('"'): continue
			l0 = re.sub("\"", "", ll[0])
			l0 = re.sub("[^a-z ]", "", l0)
			if l0 in dup_yet.keys():
				print("Uh oh, line", line_num, "/", cur_table, "has", l0, "which duplicates line", dup_yet[l0], "/", t2d[l0])
				dupes = dupes + 1
			dup_yet[l0] = line_num
			t2d[l0] = cur_table

print(dupes, "total duplicates.")