from collections import defaultdict
from shutil import copy
import os
import sys

ignore_sort = defaultdict(lambda:defaultdict(str))
table_sort = defaultdict(lambda:defaultdict(str))
default_sort = defaultdict(str)

def process_table_array(orig_file, sort_orders, table_rows, file_stream):
	table_rows = sorted(table_rows)
	file_stream.write('\n'.join(table_rows) + '\n')


def table_alf_one_file(f, launch=False, copy_over=False):
	if f not in table_sort.keys() and f not in default_sort.keys():
		print(f, "has no table sort keys or default sorts. Returning.")
		return
	f2 = f + "2"
	row_array = []
	need_head = False
	in_table = False

	print("Writing", f)

	temp_out = open(f2, "w", newline="\n")
	has_default = f in default_sort.keys()
	with open(f) as file:
		for line in file:
			if need_head:
				temp_out.write(line)
				need_head = False
				continue
			if in_table:
				if line.startswith("\[") or not line.strip():
					process_table_array(f, table_sort[f][cur_table], row_array, temp_out)
					in_table = False
					temp_out.write(line)
				else:
					row_array.append(line.strip())
				continue
			if not in_table and line.startswith('table'):
				if has_default:
					for x in ignore_sort[f].keys():
						if x in line:
							temp_out.write(line)
							continue
					cur_table = line
					temp_out.write(line)
					in_table = True
					row_array = []
					need_head = True
					continue
			temp_out.write(line)
	if in_table:
		if line.startswith("\[") or not line.strip():
			process_table_array(f, table_sort[f][cur_table], row_array, temp_out)
			in_table = False
			temp_out.write(line)
	temp_out.close()
	print("Done writing", f)
	if launch:
		os.system("wm \"{:s}\" \"{:s}\"".format(f, f2))
	if copy_over:
		copy(f2, f)

default_sort["c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Put It Up Tables.i7x"] = "0"

copy_over = False
launch_dif = True
table_alf_one_file("c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Put It Up Tables.i7x", launch_dif, copy_over)
