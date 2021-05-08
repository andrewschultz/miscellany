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
import mytools as mt

ignore_sort = defaultdict(lambda:defaultdict(str))
fix_first_line = defaultdict(lambda:defaultdict(str))
table_sort = defaultdict(lambda:defaultdict(str))
default_sort = defaultdict(str)
files_read = defaultdict(str)
need_to_catch = defaultdict(lambda:defaultdict(str))
okay = defaultdict(lambda:defaultdict(str))
err_line = defaultdict(int)

onoff = ['off', 'on']

table_default_file = "c:/writing/scripts/talf.txt"

check_apostrophes = True
force_dupe_check = False
popup_err = False
copy_over = False
launch_dif = True
override_source_size_differences = False
override_omissions = False
show_ignored = False
zap_apostrophes = False
verbose = False
story_only = table_only = story_and_tables = False
check_shifts = False

ignored_tables = ""

force_lower = True

def usage():
    print("-l/-nl decides whether or not to launch, default is {}.".format(onoff[launch_dif]))
    print("-c/-nc decides whether or not to copy back over, default is {}.".format(onoff[copy_over]))
    print("-co/-oc/-lo/-ol = only copy or launch.")
    print("-ca and -can/-nca = toggle check apostrophes.")
    print("-cs = check # of shifts e.g. 123406785 has 2.")
    print("-os overrides size differences.")
    print("-oo overrides tables omitted from the data file")
    print("-e edits the data file. -ec edits the code file.")
    print("-si shows all ignored tables.")
    print("-so means story only.")
    print("-to means table file only.")
    print("-p = popup on error.")
    print("-nf-fn and -fl/-lf toggle forcing to lower for sorting, which is on by default.")
    print("You can use a list of projects or an individual project abbreviation.")
    exit()

def get_line_dict(file_name, flag_dupes = False):
    lines_dict = defaultdict(int)
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if '"' not in line: continue
            ll = line.lower().strip()
            if ll in lines_dict:
                if flag_dupes:
                    print("WARNING line {0} <{1}> already defined.".format(line_count, line[:40].strip()))
                    mt.add_postopen_file_line(file_name, line_count)
            else:
                lines_dict[ll] = line_count
    return lines_dict

def crude_check_line_shifts(f1, f2):
    f1_lines = get_line_dict(f1, flag_dupes = False)
    f2_lines = get_line_dict(f2, flag_dupes = True)
    f1b = os.path.basename(f1)
    f2b = os.path.basename(f2)
    total_diff = 0
    line_diff = 0
    for x in f1_lines:
        if f1_lines[x] != f2_lines[x]:
            total_diff += 1
            line_diff += abs(f1_lines[x] - f2_lines[x])
    if not total_diff and not force_dupe_check:
        print("Oops, line shift checking turned up nothing. This is a bug. Bailing so you can see what happened before the file is copied over. You can run without line shifting checks to copy over.")
        sys.exit()
    print("Crude differences between {0} and {1}: {2} shifts, {3} total line-delta.".format(f1b, f2b, total_diff, line_diff))

def tab(a, b, c, zap_apostrophes = False, leave_between_parens = False): # b = boolean i = integer q = quote l = lower case u=keep upper cse for sorting e=e# for BTP a=activation of
    # print(a, b, c, zap_apostrophes)
    if leave_between_parens: a = re.sub("[\(\)]", "", a)
    else: a = re.sub("\([^\)]*\)", "", a)
    if force_lower and 'u' not in c: a = a.lower()
    elif 'k' in c: pass
    elif 'l' in c: a = a.lower()
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
                sys.exit()
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
                sys.exit()
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
        if zap_apostrophes: r = re.sub("('|\['\])", "", r, 0, re.IGNORECASE)
        else: r = re.sub("^('|\['\])", "", r, 0, re.IGNORECASE)
        r = re.sub("^(the|a|an|\() ", "", r, 0, re.IGNORECASE)
        r = re.sub("\['\]", "", r, 0, re.IGNORECASE)
        r = re.sub("-", " ", r, 0, re.IGNORECASE)
        r = re.sub("\".*", "", r, 0, re.IGNORECASE)
        r = re.sub(",", "", r, 0, re.IGNORECASE)
        r = re.sub("[\(\)!\?\.:]", " ", r, 0, re.IGNORECASE)
        r = re.sub("  +", " ", r, 0, re.IGNORECASE)
        r = re.sub("^ +", "", r, 0, re.IGNORECASE)
        return r
    return ary[b]

def note_deltas(my_ary):
    # from https://www.geeksforgeeks.org/minimum-insertions-sort-array/
    l_ary = len(my_ary)
    lis = [1] * l_ary
    for i in range(1, l_ary):
        for j in range(i):
            if (my_ary[i] >= my_ary[j] and
                lis[i] < lis[j] + 1):
                lis[i] = lis[j] + 1
    max = 0
    for i in range(l_ary):
        if (max < lis[i]):
            max = lis[i]
    return (l_ary - max)

def process_table_array(sort_orders, table_rows, file_stream):
    # print(sort_orders)
    # print(type(sort_orders), sort_orders)
    # print(type(table_rows), table_rows)
    ret_val = 0
    tr_before = defaultdict(int)
    count = 0
    for x in table_rows:
        tr_before[x] = count
        count += 1
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
        # print("Before:")
        #print(q, sort_orders, my_col, my_type)
        # for y in table_rows: print(">>", y, "/", my_col, "/", my_type, "/", tab(y, my_col, my_type))
        table_rows = sorted(table_rows, key = lambda x:tab(x, my_col, my_type, zap_apostrophes), reverse=reverse_order)
        tr = []
    for x in table_rows:
        tr.append(tr_before[x])
    if check_shifts:
        ret_val = note_deltas(tr)
        # print("After:")
        # print('\n'.join(table_rows) + '\n')
    file_stream.write('\n'.join(table_rows) + '\n')
    return ret_val

def read_table_and_default_file():
    cur_file = ""
    line_count = 0
    prev_def = defaultdict(int)
    found_unknown = False
    with open(table_default_file) as file:
        for (line_count, line) in enumerate(file, 1):
            ll = line.lower().strip()
            if not ll: continue
            if line.startswith('#'): continue
            if line.startswith(';'): break
            if '=' in line:
                if '/' in line and "default" not in line: print("WARNING", table_default_file, "line", line_count, "has forward slashes but needs backward slashes.")
                (left_side, right_side) = mt.cfg_data_split(line)
                right_side = re.sub("/", "\\\\", right_side).lower()
                right_side_fwd = re.sub(r"\\", r"/", right_side)
                if left_side == 'f' or left_side == 'file':
                    cur_file = right_side
                elif left_side == "okay":
                    if right_side in okay[cur_file].keys():
                        print("BAILING double assignment of okay for", right_side, "in", cur_file, "at line", line_count)
                        exit()
                    okay[cur_file][right_side] = True
                    need_to_catch[cur_file][right_side] = True
                elif left_side == "fixfirst":
                    if right_side in fix_first_line[cur_file].keys():
                        print("BAILING double assignment of ignore for", right_side, "in", cur_file, "at line", line_count)
                        exit()
                    #print("Fixing first line for {} in {}.".format(right_side, cur_file))
                    fix_first_line[cur_file][right_side] = True
                    need_to_catch[cur_file][right_side] = True
                elif left_side == "ignore":
                    if right_side in ignore_sort[cur_file].keys():
                        print("BAILING double assignment of ignore for", right_side, "in", cur_file, "at line", line_count)
                        exit()
                    ignore_sort[cur_file][right_side] = True
                    need_to_catch[cur_file][right_side] = True
                elif left_side == "default":
                    if not cur_file:
                        print("WARNING defined default with no cur_file at line", line_count)
                        continue
                    if cur_file in default_sort.keys():
                        print("WARNING: ignoring redefined default sort for", cur_file," at line", line_count, "previous line", prev_def[line_count])
                        continue
                    default_sort[cur_file] = right_side_fwd
                    prev_def[cur_file] = line_count
                else:
                    print("Unknown = at line", line_count, ll)
                    found_unknown = True
                continue
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
    if found_unknown:
        sys.exit("Fix unknown prefixes in talf.txt and rerun.")

def got_match(full_table_line, target_dict):
    for elt in target_dict.keys():
        if elt in full_table_line:
            return elt
    return ''

def table_alf_one_file(f, launch=False, copy_over=False):
    return_val = 0
    total_shifts = 0
    total_tables = 0
    if story_and_tables:
        if 'story' not in f.lower() and 'table' not in f.lower(): return 0
    elif story_only and 'story' not in f.lower(): return 0
    elif table_only and 'table' not in f.lower(): return 0
    global ignored_tables
    cur_table = ''
    match_table = ''
    if f not in default_sort.keys() and len(ignore_sort[f].keys()) > 0:
        print("WARNING you have ignored tables but no default value. Wiping out ignored tables.")
        for x in ignore_sort[f].keys():
            need_to_catch[f].pop(x)
        ignore_sort[f].clear()
    f2 = f + "2"
    fb = os.path.basename(f)
    f2b = os.path.basename(f2)
    if f not in table_sort.keys() and f not in default_sort.keys():
        print("WARNING: no table sort keys/default sorts for {0}. Returning. If you are looking for something in this file, you may wish to check for slash directions.".format(fb.upper()))
        if ("/" in f and "\\" in f) or re.sub("\\\\", "/", f) in default_sort.keys() or re.sub("/", "\\\\", f) in default_sort.keys(): #?? this can be fixed
            print("NOTE: brief check shows", f, "very likely has slashes normalized badly.")
        return 0
    files_read[f] = True
    row_array = []
    need_head = False
    need_extra_head = False
    in_sortable_table = False
    in_table = False
    if verbose: print("Inspecting", f)
    temp_out = open(f2, "w", newline="\n")
    has_default = f in default_sort.keys()
    tabs_this_table = 0
    err_line.clear()
    apostrophe_errors = 0
    with open(f) as file:
        for (line_count, line) in enumerate(file, 1):
            if need_head:
                if match_table in fix_first_line[f]:
                    print("Ignoring first line of", match_table)
                    need_extra_head = True
                    need_to_catch[f].pop(match_table)
                temp_out.write(line)
                tabs_this_table = len(line.split("\t"))
                need_head = False
                continue
            if need_extra_head:
                need_extra_head = False
                temp_out.write(line)
                continue
            if check_apostrophes and in_table:
                this_apostrophe = i7.apostrophe_check_line(line, True, f, line_count)
                if this_apostrophe:
                    apostrophe_errors += this_apostrophe
                    if not copy_over:
                        print("Iffy apostrophe", f, line_count)
                        mt.add_postopen(f, line_count, priority=8)
            if in_sortable_table:
                if line.count("\"") % 2 and 'ibq' not in line:
                    print("Odd number of quotes at line {:d}: {:s}".format(line_count, line))
                    i7.npo(f, line_count)
                if re.search("ends here(\.)?$", line):
                    print("Final table needs space before indicating header file ends.")
                    i7.npo(f, line_count)
                if line.startswith("[") or not line.strip():
                    temp = process_table_array(what_to_sort, row_array, temp_out)
                    if temp:
                        total_tables += 1
                        total_shifts += temp
                        print(fb, match_table, "had {0} shift{1}".format(temp, mt.plur(temp)))
                    # print("Wrote", cur_table)
                    in_sortable_table = False
                    in_table = False
                    row_array = []
                    temp_out.write(line)
                elif tabs_this_table > 1 and len(line.split("\t")) == 1 and not line.startswith("\""):
                    print("It looks like you put in a non-table comment at line {}: {}".format(line_count, ":", line.strip()))
                    i7.npo(f, line_count)
                else:
                    row_array.append(line.strip())
                    err_line[line.strip().lower()] = line_count
                continue
            if in_table:
                if line.startswith("[") or not line.strip():
                    temp_out.write(line)
                    in_table = False
                    continue
            if not in_table and line.startswith('table of '):
                in_table = True
                cur_table = got_match(line, table_sort[f])
                match_table = re.sub(" *\[.*", "", line.lower().strip())
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
                        ignored_tables = ignored_tables + "{:s} Line {:d} (DIRECTED): {:s}".format(fb, line_count, line)
                        print("Ignoring {:s} file default for {:s}{:s}.".format(fb, cur_table, ("/ " + line.strip() if cur_table != line else "")))
                        # print("Zapping", x, "from", fb)
                        if "(continued)" not in line:
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
                ignored_tables = ignored_tables + "{:s} Line {:d} ({:s}): {:s}".format(fb, line_count,
                  "OKAY DIF" if got_match(line, okay[f]) else ("DEFAULT " if has_default else "PASSTHRU"), line)
            # if line.startswith("table"): print(">>", line.strip())
            temp_out.write(line)
    if in_sortable_table:
        # if line.startswith("["): print(line)
        if line.startswith("\[") or not line.strip():
            temp = process_table_array(table_sort[f][cur_table], row_array, temp_out)
            if temp:
                total_tables += 1
                total_shifts += temp
                print(fb, match_table, "had", temp, "shift{0}".format(mt.plur(temp)))
            in_sortable_table = False
            temp_out.write(line)
    temp_out.close()
    if apostrophe_errors: print("{} errors found in {}.".format(apostrophe_errors, fb))
    if verbose: print("Done writing to", f2b)
    forgot_to_catch = False
    for x in files_read.keys():
        if len(need_to_catch[x]) > 0:
            print(os.path.basename(x), "had leftover table-sort key" + ('s' if len(need_to_catch[x]) > 1 else '') + ":", ','.join(sorted(need_to_catch[x].keys())))
            forgot_to_catch = True
        else:
            print(os.path.basename(x), "had no leftover table-sort keys")
    if forgot_to_catch:
        if override_omissions:
            print("Ignoring unaccessed tables.")
        else:
            print("You need to sort out the unaccessed tables in talf.txt before I copy back over.")
            sys.exit()
    if total_tables:
        print("{0} table{1} shifted, {2} line{3} shifted in {4}.".format(total_tables, mt.plur(total_tables), total_shifts, mt.plur(total_shifts), fb))
    files_identical = cmp(f, f2)
    identical_ignoring_eol = mt.compare_unshuffled_lines(f, f2)
    identical_when_shuffled = mt.compare_shuffled_lines(f, f2)
    if copy_over:
        if cmp(f, f2):
            print("NO DIFFERENCES FOUND. Not copying over.")
            if force_dupe_check:
                crude_check_line_shifts(f2, f)
        elif identical_ignoring_eol:
            print("Only line break differences found. Not copying over.")
            if force_dupe_check:
                crude_check_line_shifts(f2, f)
        elif identical_when_shuffled:
            print("DIFFERENCES IN ORDER BUT NOT CONTENT FOUND. Copying over.")
            if check_shifts:
                print("Total tables shifted: {0}. Total insertion shifts: {1}.".format(total_tables, total_shifts))
                crude_check_line_shifts(f2, f)
            copy(f2, f)
            return_val = 1
        elif override_source_size_differences:
            print("Copying over despite potential information loss.")
            copy(f2, f)
            return_val = 1
        else:
            print("Potential information loss. Use -os to override this. {} kept for inspection.".format(f2b))
            return_val = 1
        os.remove(f2)
    else:
        if identical_ignoring_eol:
            print("Only line break differences found. No need to copy over.")
            os.remove(f2)
        elif identical_when_shuffled:
            print("MEANINGFUL SORTABLE DIFFERENCES FOUND. Temp file not deleted. Run with -c to copy back over or -l to launch differences.")
    if launch:
        if not os.path.exists(f2):
            print("Not launching differences because there were no differences.")
        elif cmp(f, f2) or identical_ignoring_eol:
            print("NO MEANINGFUL DIFFERENCE, NOT LAUNCHING WINDIFF")
            os.remove(f2)
        else:
            if identical_ignoring_eol:
                print("Oops, minor error, should have deleted", f2)
                os.remove(f2)
            else:
                print("LAUNCHING DIFFERENCE:")
                mt.wm(f, f2)
    return return_val

cmd_count = 1
projects = []

while cmd_count < len(sys.argv):
    a1 = sys.argv[cmd_count].lower()
    arg = mt.nohy(sys.argv[cmd_count].lower())
    if a1 in i7.i7com.keys():
        projects.extend(i7.i7com[arg].split(","))
    elif a1 in i7.i7x.keys():
        projects.append(i7.i7x[arg])
    elif a1 in i7.i7xr.keys():
        projects.append(arg)
    elif arg == 'l': launch_dif = True
    elif arg == 'nl': launch_dif = False
    elif arg == 'p': popup_err = True
    elif arg == 'np': popup_err = False
    elif arg == 'c': copy_over = True
    elif arg == 'co' or arg == 'oc':
        copy_over = True
        launch_dif = False
    elif arg == 'lo' or arg == 'ol':
        copy_over = False
        launch_dif = True
    elif arg == 'cs': check_shifts = True
    elif arg == 'ca': check_apostrophes = True
    elif arg == 'nca' or arg == 'can': check_apostrophes = False
    elif arg == 'ec': open_source()
    elif arg == 'e': os.system(table_default_file)
    elif arg == 'os': override_source_size_differences = True
    elif arg == 'oo': override_omissions = True
    elif arg == 'si': show_ignored = True
    elif arg == 'so': story_only = True
    elif arg == 'to': table_only = True
    elif arg == 'ts' or arg == 'st': story_and_tables = True
    elif arg == 'v': verbose = True
    elif arg == 'nc': copy_over = False
    elif arg == 'za': zap_apostrophes = True
    elif arg == 'fl' or arg == 'lf': force_lower = True
    elif arg == 'fn' or arg == 'nf': force_lower = False
    elif arg == 'fd': force_dupe_check = True
    elif arg == '?': usage()
    else:
        print(arg, "is an invalid parameter.")
        usage()
    cmd_count += 1

if story_only + table_only + story_and_tables: sys.exit("Options crossed -so, -to, -ts/-st ... can only have one.")

projset = set(projects)
diff = len(projects) - len(projset)

if len(projects) == 0:
    d2p = i7.dir2proj()
    if d2p:
        print("Using default project", d2p, "since you're in that directory.")
        projects = [ d2p ]
    else:
        print("Need to write in a project.")
        exit()

if diff > 0:
    print(diff, "duplicate project" + ("s" if diff > 1 else ""), "weeded out")
    projects = list(projset)

read_table_and_default_file()

return_value = 0

for x in projects:
    if x not in i7.i7f:
        print("WARNING for project {x}: you need to define which header files have tables in project", x, "via i7p.txt.")
        continue
    for y in i7.i7f[x]:
        return_value += table_alf_one_file(y.lower(), launch_dif, copy_over)

if show_ignored:
    if ignored_tables:
        print("=====================IGNORED TABLES")
        print(ignored_tables.strip())
    else:
        print("=====================NO IGNORED TABLES")

mt.postopen_files(bail_after=False)

sys.exit(return_value)
