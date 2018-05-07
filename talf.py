#
# talf.py
#
# table alphabetizer/sorter in python
#
# -c = copy back over
# -l = launch
# -si = verbose what happened

from collections import defaultdict
from shutil import copy
from filecmp import cmp
import os
import sys
import i7
import re
import ctypes

ignore_sort = defaultdict(lambda:defaultdict(str))
table_sort = defaultdict(lambda:defaultdict(str))
default_sort = defaultdict(str)
files_read = defaultdict(str)
need_to_catch = defaultdict(lambda:defaultdict(str))
okay = defaultdict(lambda:defaultdict(str))
err_line = defaultdict(int)

onoff = ['off', 'on']

table_default_file = "c:/writing/scripts/talf.txt"

popup_err = False
copy_over = False
launch_dif = True
override_source_size_differences = False
override_omissions = False
show_ignored = False

ignored_tables = ""

def usage():
    print("-l/-nl decides whether or not to launch, default is", onoff[copy_over])
    print("-c/-nc decides whether or not to copy back over, default is", onoff[copy_over])
    print("-os overrides size differences")
    print("-oo overrides tables omitted from the data file")
    print("-e edits the data file. -ec edits the code file.")
    print("-si shows all ignored tables.")
    print("-p = popup on error.")
    print("You can use a list of projects or an individual project abbreviation.")
    exit()

force_lower = True

def tab(a, b, c): # b = boolean i = integer q = quote l = lower case e=e# for BTP a=activation of
    if force_lower:
        a = a.lower()
    if 'k' in c:
        pass
    elif 'l' in c:
        a = a.lower()
    ary = re.split("\t+", a)
    orig = ary[b]
    ret = ary[b]
    if 'b' in c:
        return ary[b].lower() == 'true'
    if 'a' in c:
        if "[activation of" not in ary[b]:
            if "[na]" in ary[b]:
                return("zzzz" + re.sub("\"", "", ary[b]))
            if "[na " not in ary[b]:
                print("Bad activation/na:", orig)
                if popup_err:
                    messageBox = ctypes.windll.user32.MessageBoxW
                    messageBox(None, 'Did not sort\n{:s}\n{:d}'.format(a, err_line[a.lower()]), 'Problems sorting stuff', 0x0)
                exit()
            return("zz" + re.sub(".*\[na ", "", ary[b]))
        arb = re.sub("^.*?activation of ", "", ary[b])
        new_ary = re.split("activation of ", arb)
        newer_ary = sorted([re.sub("\].*", "", x) for x in new_ary])
        # if len(newer_ary) > 1: print(newer_ary)
        return newer_ary[0]
    if 'e' in c:
        if not re.search("\[e[1-9]\]", ary[b]):
            if not re.search("\[na\]", ary[b]):
                print("BAD LINE", orig)
                exit()
            ret = re.sub("\"", "", ary[b])
            return ret
        else:
            final_ary = []
            to_go = re.sub("[\?\.\!,]", "", ret)
            to_go = re.sub("^\"", "", to_go)
            to_go = re.sub("'?\".*", "", to_go) # make sure comments outside quotes don't get snagged
            while "[e" in to_go:
                r = re.sub("^.*?\[e", "", to_go)
                r = re.sub("\].*", "", r)
                r2 = int(r)
                to_go_prev = to_go
                to_go = re.sub("^.*?\[e[0-9]\]", "", to_go)
                if to_go_prev == to_go:
                    print(ret, "blew things up, with", to_go)
                    exit()
                temp = re.sub("\[e.*", "", to_go)
                new_ary = re.split("[ -]", temp)
                if r2 > len(new_ary):
                    print("Too-small e-value for ", new_ary, "out of", temp, "in", orig, r2, ">", len(new_ary))
                    exit()
                final_ary.append(temp)
            if len(final_ary) == 0:
                print(ret, "gave no final array. Bailing.")
                exit()
            final_ary = sorted(final_ary)
            return final_ary[0]
    if 'i' in c:
        try:
            return int(ary[b])
        except:
            return 0
    if 'q' in c:
        r = re.sub("^\"", "", ary[b].lower(), 0, re.IGNORECASE)
        r = re.sub("^[the|a|\(] ", "", r, 0, re.IGNORECASE)
        r = re.sub("\".*", "", r, 0, re.IGNORECASE)
        return r
    return ary[b]

def process_table_array(sort_orders, table_rows, file_stream):
    # print(sort_orders)
    # print(type(sort_orders), sort_orders)
    # print(type(table_rows), table_rows)
    for q in sort_orders:
        ary = q.split('/')
        my_type = ''
        my_col = 0
        try:
            my_col = int(ary[0])
        except:
            print("Need integer in first value of", q)
        if len(ary) > 1:
            my_type = ary[1]
        reverse_order = len(ary) > 2 and ary[2] == 'r'
        count = 0
        for y in table_rows:
            count += 1
        # print("Before:")
        #print(q, sort_orders, my_col, my_type)
        # for y in table_rows: print(">>", y, "/", my_col, "/", my_type, "/", tab(y, my_col, my_type))
        table_rows = sorted(table_rows, key = lambda x:tab(x, my_col, my_type), reverse=reverse_order)
        # print("After:")
        # print('\n'.join(table_rows) + '\n')
    file_stream.write('\n'.join(table_rows) + '\n')

def read_table_and_default_file():
    cur_file = ""
    line_count = 0
    prev_def = defaultdict(int)
    with open(table_default_file) as file:
        for line in file:
            line_count += 1
            ll = line.lower().strip()
            if not ll: continue
            if line.startswith('#'): continue
            if line.startswith(';'): break
            if '=' in line:
                if line != line.lower(): print("WARNING", table_default_file, "line", line_count, "has upper case letters but shouldn't.")
                if '/' in line: print("WARNING", table_default_file, "line", line_count, "has forward slashes but needs backward slashes.")
                right_side = re.sub(".*=", "", ll)
                right_side = re.sub("/", "\\\\", right_side)
                right_side = right_side.lower()
                right_side_fwd = re.sub(r"\\", r"/", right_side)
                if ll.startswith("f="):
                    cur_file = right_side
                    continue
                if ll.startswith("file="):
                    cur_file = right_side
                    continue
                if ll.startswith("okay="):
                    if right_side in okay[cur_file].keys():
                        print("BAILING double assignment of okay for", right_side, "in", cur_file, "at line", line_count)
                        exit()
                    okay[cur_file][right_side] = True
                    need_to_catch[cur_file][right_side] = True
                    continue
                if ll.startswith("ignore="):
                    if right_side in ignore_sort[cur_file].keys():
                        print("BAILING double assignment of ignore for", right_side, "in", cur_file, "at line", line_count)
                        exit()
                    ignore_sort[cur_file][right_side] = True
                    need_to_catch[cur_file][right_side] = True
                    continue
                if line.lower().startswith("default="):
                    if not cur_file:
                        print("WARNING defined default with no cur_file at line", line_count)
                        continue
                    if cur_file in default_sort.keys():
                        print("WARNING: ignoring redefined default sort for", cur_file," at line", line_count, "previous line", prev_def[cur_line])
                        continue
                    default_sort[cur_file] = right_side_fwd
                    prev_def[cur_file] = line_count
                    continue
                print("Unknown = at line", line_count, ll)
                exit()
            if ':' in line:
                ary = ll.split(':')
                if ary[0] in table_sort[cur_file].keys():
                    print("BAILING double assignment of table sorting for", right_side, "in", cur_file, "at line", line_count)
                    exit()
                need_to_catch[cur_file][ary[0]] = True
                table_sort[cur_file][ary[0]] = ary[1]
                # print(ary[0], "goes to", ary[1])
            else:
                print("Line", line_count, "needs :")

def got_match(full_table_line, target_dict):
    for elt in target_dict.keys():
        if elt in full_table_line:
            return elt
    return ''

def table_alf_one_file(f, launch=False, copy_over=False):
    global ignored_tables
    fs = os.path.basename(f)
    files_read[f] = True
    cur_table = ''
    if f not in default_sort.keys() and len(ignore_sort[f].keys()) > 0:
        print("WARNING you have ignored tables but no default value. Wiping out ignored tables.")
        for x in ignore_sort[f].keys():
            need_to_catch[f].pop(x)
        ignore_sort[f].clear()

    if f not in table_sort.keys() and f not in default_sort.keys():
        print(f, "has no table sort keys or default sorts. Returning.")
        return
    f2 = f + "2"
    row_array = []
    need_head = False
    in_sortable_table = False
    in_table = False

    print("Writing", f)

    temp_out = open(f2, "w", newline="\n")
    has_default = f in default_sort.keys()
    line_count = 0
    err_line.clear()
    with open(f) as file:
        for line in file:
            line_count += 1
            if need_head:
                temp_out.write(line)
                need_head = False
                continue
            if in_sortable_table:
                if line.startswith("[") or not line.strip():
                    process_table_array(what_to_sort, row_array, temp_out)
                    # print("Wrote", cur_table)
                    in_sortable_table = False
                    in_table = False
                    row_array = []
                    temp_out.write(line)
                else:
                    row_array.append(line.strip())
                    err_line[line.strip().lower()] = line_count
                continue
            if in_table:
                if line.startswith("[") or not line.strip():
                    temp_out.write(line)
                    in_table = False
                    continue
            if not in_table and line.startswith('table'):
                in_table = True
                cur_table = got_match(line, table_sort[f])
                if cur_table:
                    need_to_catch[f].pop(cur_table)
                    # print("Zapping", cur_table, "from", f)
                    what_to_split = table_sort[f][cur_table]
                    what_to_sort = what_to_split.split(',')
                    temp_out.write(line)
                    # if line.startswith("table"): print(">>", line.strip())
                    in_sortable_table = True
                    row_array = []
                    need_head = True
                    continue
                if has_default:
                    temp_out.write(line)
                    cur_table = got_match(line, ignore_sort[f])
                    if cur_table:
                        ignored_tables = ignored_tables + "{:s} Line {:d} (DIRECTED): {:s}".format(fs, line_count, line)
                        print("Ignoring default for table", cur_table, ("/ " + line if cur_table != line else ""))
                        # print("Zapping", x, "from", os.path.basename(f))
                        need_to_catch[f].pop(cur_table)
                        continue
                    what_to_split = default_sort[f]
                    what_to_sort = what_to_split.split(',')
                    in_sortable_table = True
                    need_head = True
                    continue
                if got_match(line, okay[f]):
                    need_to_catch[f].pop(got_match(line, okay[f]))
                    temp_out.write(line)
                    continue
                ignored_tables = ignored_tables + "{:s} Line {:d} ({:s}): {:s}".format(fs, line_count,
                  "OKAY DIF" if got_match(line, okay[f]) else ("DEFAULT " if has_default else "PASSTHRU"), line)
            # if line.startswith("table"): print(">>", line.strip())
            temp_out.write(line)
    if in_sortable_table:
        # if line.startswith("["): print(line)
        if line.startswith("\[") or not line.strip():
            process_table_array(table_sort[f][cur_table], row_array, temp_out)
            in_sortable_table = False
            temp_out.write(line)
    temp_out.close()
    print("Done writing to", os.path.basename(f2))
    if launch:
        if cmp(f, f2):
            print("NO DIFFERENCE, NOT LAUNCHING DIFFERENCE")
        else:
            print("LAUNCHING DIFFERENCE:")
            os.system("wm \"{:s}\" \"{:s}\"".format(f, f2))
    forgot_to_catch = False
    for x in files_read.keys():
        if len(need_to_catch[x]) > 0:
            print(os.path.basename(x), "had leftover table-sort key" + ('s' if len(need_to_catch[x]) > 1 else '') + ":", ','.join(sorted(need_to_catch[x].keys())))
            forgot_to_catch = True
        else:
            print(os.path.basename(x), "is okay")
    if forgot_to_catch:
        if override_omissions:
            print("Ignoring unaccessed tables.")
        else:
            print("You need to sort out the unaccessed tables in talf.txt before I copy back over.")
            exit()
    if copy_over:
        if os.path.getsize(f) != os.path.getsize(f2):
            if override_source_size_differences:
                print("Different sizes, but copying anyway.")
            else:
                print(f, '=', os.path.getsize(f), "bytes")
                print(f2, '=', os.path.getsize(f2), "bytes")
                print('Use -os to ignore this size differences, but do verify no information was lost, first.')
                exit()
        if cmp(f, f2):
            print("NO DIFFERENCES FOUND. Not copying over.")
        else:
            print("DIFFERENCES FOUND. Copying over.")
            copy(f2, f)
    elif not cmp(f, f2):
        print("DIFFERENCES FOUND. Run with -c to copy back over.")

count = 1
projects = []
while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg in i7.i7c.keys():
        projects = projects + i7.i7c[arg]
        count += 1
        continue
    elif arg in i7.i7x.keys():
        projects.append(i7.i7x[arg])
        count += 1
        continue
    if arg.startswith('-'): arg = arg[1:]
    if arg == 'l':
        launch_dif = True
    elif arg == 'nl':
        launch_dif = False
    elif arg == 'p':
        popup_err = True
    elif arg == 'np':
        popup_err = False
    elif arg == 'c':
        copy_over = True
    elif arg == 'ec':
        open_source()
    elif arg == 'e':
        os.system(table_default_file)
    elif arg == 'os':
        override_source_size_differences = True
    elif arg == 'oo':
        override_omissions = True
    elif arg == 'si':
        show_ignored = True
    elif arg == 'nc':
        copy_over = False
    elif arg == '?':
        usage()
    else:
        print(arg, "is an invalid parameter.")
        usage()
    count += 1

projset = set(projects)
diff = len(projects) - len(projset)

if len(projects) == 0:
    print("Need to write in a project.")
    exit()

if diff > 0:
    print(diff, "duplicate project" + ("s" if diff > 1 else ""), "weeded out")
    projects = list(projset)

read_table_and_default_file()

for x in projects:
    for y in i7.i7f[x]:
        table_alf_one_file(y.lower(), launch_dif, copy_over)

if show_ignored:
    if ignored_tables:
        print("=====================IGNORED TABLES")
        print(ignored_tables.strip())
    else:
        print("=====================NO IGNORED TABLES")
