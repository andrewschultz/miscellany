from collections import defaultdict
from shutil import copy
import os
import sys
import i7

ignore_sort = defaultdict(lambda:defaultdict(str))
table_sort = defaultdict(lambda:defaultdict(str))
default_sort = defaultdict(str)

onoff = ['off', 'on']

copy_over = False
launch_dif = True
def usage():
    print("-l/-nl decides whether or not to launch, default is", onoff[copy_over])
    print("-c/-nc decides whether or not to copy back over, default is", onoff[copy_over])
    print("You can use a list of projects or an individual project abbreviation.")
    exit()

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

count = 1
projects = []
while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg in i7.i7c.keys():
        projects = projects + i7.i7c[arg]
        count = count + 1
        continue
    elif arg in i7.i7x.keys():
        projects.append(i7.i7x[arg])
        count = count + 1
        continue
    if arg.startswith('-'): arg = arg[1:]
    if arg == 'l':
        launch_dif = True
    elif arg == 'nl':
        launch_dif = False
    elif arg == 'c':
        copy_over = True
    elif arg == 'nc':
        copy_over = False
    elif arg == '?':
        usage()
    else:
        print(arg, "is an invalid parameter.")
        usage()
    count = count + 1

projset = set(projects)
diff = len(projects) - len(projset)

if diff > 0:
    print(diff, "duplicate project" + ("s" if diff > 1 else ""), "weeded out")
    projects = list(projset)

default_sort["c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Put It Up Tables.i7x"] = "0"

table_alf_one_file("c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Put It Up Tables.i7x", launch_dif, copy_over)
