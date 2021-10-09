# ott.py: organize table text

import exrex
import sys
import mytools as mt
import re
import i7
from collections import defaultdict
from shutil import copy

main_check = defaultdict(tuple)
auxil_check = defaultdict(tuple)
files_with_tables = defaultdict(list)

ott_temp = "c:/writing/temp/ott-py-tempfile.txt"
ott_cfg = "c:/writing/scripts/ott.txt"

print_what_to_do = True
write_out = True
copy_back = False

in_loop = False
squash_errors = False

default_proj = ''
my_proj = i7.dir2proj()

ignores = defaultdict(lambda: defaultdict(bool))
onces = defaultdict(lambda: defaultdict(bool))
tables_to_check = defaultdict(lambda: defaultdict(bool))

# for later
# import exrex
# full_regex = 'table of {} (anagrams|hintobjs)'.format(my_reg)
# sys.exit(list(exrex.generate(full_regex)))

def is_valid_table_header(x):
    return x.lower() in tables_to_check[my_proj]

def check_my_loop(my_loop):
    loop_verified = True
    for x in main_check:
        if x not in auxil_check:
            if x in onces[my_proj] and onces[my_proj][x]:
                continue
            if loop_verified:
                print("ERRORS FOR", my_loop)
            loop_verified = False
            print("Auxiliary text for", x, "should be placed after", my_loop)
    for x in auxil_check:
        if x not in main_check:
            if loop_verified:
                print("ERRORS FOR", my_loop)
            loop_verified = False
            print("Stray to-say or rule:", x, auxil_check[x])
    if loop_verified:
        print("Hooray! Loop verified for {}!".format(my_loop))
    y = list(set(main_check) & set(auxil_check))
    y = sorted(y, key = main_check.get)
    y0 = sorted(y, key = auxil_check.get)
    for z in range(0, len(y) - 1):
        if auxil_check[y[z+1]] < auxil_check[y[z]]:
            print("Out of order: {} {} should (probably) be placed just before {} {}.".format(y[z], auxil_check[y[z]], y[z+1], auxil_check[y[z+1]]))
    if len(y) == len(y0):
        max = -1
        min = -1
        for z in range(0, len(y)):
            if y[z] != y0[z]:
                if min == -1:
                    min = z
                max = z + 1
        if min > -1:
            print("Comparing arrays")
            for z in range(min, max):
                print(y0[z], "should change", y.index(y0[z]) - z, "to between", "start" if z == 0 else y[y.index(y0[z]) - 1], "and", "end" if y.index(y0[z]) == len(y0) - 1 else y[y.index(y0[z]) + 1])
                #print(z, y0[z], '->', y[z])

def invalid_sub(my_text):
    if my_text.startswith("if ") or my_text.startswith("unless ") or my_text.startswith("else if "):
        return True
    return False

def slate_for_sorting(my_string):
    if my_string in ignores['global']:
        return False
    if my_string in ignores[my_proj]:
        return False
    return True

def define_finds(my_entry, my_line, my_col, current_table):
    fall = re.findall(r'\[(.*?)\]', my_entry)
    my_index = 0
    if (fall):
        for q in fall:
            if q.startswith('the '):
                q = q[4:]
            q0 = re.sub(" of .*", "", q)
            if q0 not in main_check and slate_for_sorting(q0) and not invalid_sub(q0):
                my_index += 1
                main_check[q0] = (my_line, my_col, current_table, my_index)
    if my_entry.endswith(" rule") and my_entry != "a rule":
        if my_entry not in main_check:
            main_check[my_entry] = (my_line, my_col, current_table, 0)

def find_ignores():
    cur_proj = 'global'
    with open(ott_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith('#'):
                continue
            (prefix, data) = mt.cfg_data_split(mt.zap_comments(line))
            ary = mt.zap_comments(line.strip()).split(',')
            if prefix == 'proj':
                cur_proj = i7.long_name(data)
                print("New proj", cur_proj)
                continue
            elif prefix == 'file_list':
                for x in data.split(","):
                    if x == 'ni':
                        files_with_tables.append(i7.main_src(cur_proj))
                    else:
                        files_with_tables.append(i7.hdr(cur_proj, x))
                continue
            elif prefix == 'ignore':
                for x in data.split(","):
                    if x in ignores[cur_proj]:
                        print("Duplicate ignore <{}> at {}.".format(x, line_count))
                    else:
                        ignores[cur_proj][x] = True
            elif prefix == 'once':
                if cur_proj == 'global':
                    print("WARNING a once function should not be part of a global project line {}: {}".format(line_count, line.strip()))
                for x in data.split(","):
                    if x in onces[cur_proj]:
                        print("Duplicate ignore <{}> at {}.".format(x, line_count))
                    else:
                        onces[cur_proj][x] = True
            elif prefix == 'tables_add':
                to_add = exrex.generate(data)
                for mytab in to_add:
                    if mytab in tables_to_check:
                        print("Duplicate table_to_check {} for project {} from table extension at line {}.".format(mytab, cur_proj, line_count))
                    else:
                        tables_to_check[cur_proj][mytab] = False

def process_sortables(my_dict, order_dict, fout, leave_cr_on_blank = True):
    if not leave_cr_on_blank and len(my_dict) == 0:
        return
    #for o in order_dict:
        #print(o, order_dict[o], type(order_dict[o]))
    for m in my_dict:
        if m not in order_dict:
            print("WARNING:", m, "is in the post-table subtitutions but not in the table. It is given a default value and kicked to the end.")
            order_dict[m] = (1<<20, 0, '', 0)
        #print(m, order_dict[m], type(order_dict[m]))
    for x in sorted(my_dict, key=order_dict.get):
        fout.write("\n" + my_dict[x])
    fout.write("\n")
    return

def shorthand_of(header_line):
    is_common_error = False
    if re.search("^(before|check|after|instead of|carry out) ", header_line):
        is_common_error = "Possible rule starting"
    if re.search("is a [-a-z ]+ that varies", header_line):
        is_common_error = "Possible variable definition"
    if is_common_error and squash_errors:
        return('', is_common_error)
    temp = header_line.strip()
    if temp.startswith("to say"):
        temp = re.sub("^to say ", "", temp.strip().lower())
        temp = re.sub(" of \(.*", "", temp)
        temp = re.sub(":.*", "", temp)
    elif ("(this is the" in header_line and "rule" in header_line) or header_line.startswith("this is the"):
        temp = re.sub("^.*?this is the ", "", temp.strip().lower())
        temp = re.sub(":.*", "", temp).strip()
    return (temp, is_common_error)

def write_dont_print(my_file):
    in_table = False
    in_sortable_section = False
    need_header = False
    current_sortable = ''
    sortable_stuff = defaultdict(str)
    fout = open(ott_temp, "w")
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if need_header:
                need_header = False
            l0 = mt.zap_comments(line)
            if in_sortable_section and (l0.startswith("book") or l0.startswith("volume") or l0.endswith("auxiliary") or (l0.startswith("table of") and not '\t' in l0)):
                process_sortables(sortable_stuff, main_check, fout)
                sortable_stuff.clear()
                main_check.clear()
                auxil_check.clear()
                in_sortable_section = False
            if is_valid_table_header(l0):
                my_table = mt.zap_comments(line.lower())
                in_table = True
                if my_table in tables_to_check[my_proj]:
                   tables_to_check[my_proj][my_table] = True
                need_header = True
            if in_table and not line.strip():
                in_table = False
                in_sortable_section = True
            if in_table and not need_header:
                ary = l0.lower().split("\t")
                for x in range(0, len(ary)):
                    define_finds(ary[x], line_count, x, current_table)
            if not in_sortable_section:
                fout.write(line)
                continue
            if not current_sortable:
                if line.strip():
                    (current_sortable, common_error) = shorthand_of(line)
                    if current_sortable in onces[my_proj]:
                        if onces[my_proj][current_sortable] == True:
                            print("WARNING {} line {} redefined sortable {} that should only appear once.".format(my_file, line_count, current_sortable))
                    if common_error:
                        print("WARNING: {} at {} line {}: {}".format(common_error, my_file, line_count, l0))
                    sortable_stuff[current_sortable] = line
            else:
                if line.strip():
                    sortable_stuff[current_sortable] += line
                else:
                    current_sortable = ''
    if len(sortable_stuff):
        process_sortables(sortable_stuff, main_check, fout)
    fout.close()
    if not mt.alfcomp(my_file, ott_temp):
        print("UH OH data loss/gain between tempfile and current one. You likely forgot to add a rule. Fix before continuing.")
        return
    else:
        print("No differences.")
    mt.wm(my_file, ott_temp)
    if copy_back:
        print("Copying back.")
        copy(ott_temp, my_file)
    else:
        print("Use -c to copy.")

def print_dont_write(my_file):
    in_loop = False
    current_table = ''
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            l0 = mt.zap_comments(line)
            if l0.startswith("table of ") and "\t" in l0:
                print("Ignoring probable table-in-table at line {}, character {}".format(line_count, l0.index("\t")))
            if l0.startswith("book") or l0.startswith("volume") or (l0.startswith("table of") and not "\t" in l0) or l0.endswith("auxiliary"):
                if current_table and in_loop:
                    check_my_loop(current_table)
                    main_check.clear()
                    auxil_check.clear()
                in_loop = False
                current_table = ''
                if is_valid_table_header(l0):
                    current_table = l0.strip()
                    #print("new table", current_table, line_count)
                continue
            if l0.startswith("table of") and not "\t" in l0:
                current_table = l0.strip()
                if current_table in tables_to_check[my_proj]:
                   tables_to_check[my_proj][current_table] = True
            if l0.endswith("auxiliary"):
                in_loop = False
                continue
            if current_table and not in_loop:
                if not l0:
                    in_loop = True
                    continue
                ary = l0.lower().split("\t")
                for x in range(0, len(ary)):
                    define_finds(ary[x], line_count, x, current_table)
                continue
            if not in_loop:
                continue
            if in_loop:
                (temp, common_error) = shorthand_of(l0)
                if common_error:
                    print("WARNING: {} at {} line {}: {}".format(common_error, my_file, line_count, l0))
                if l0.startswith("to say "):
                    if temp in auxil_check:
                        print("Duplicate to-say", temp, line_count)
                    else:
                        auxil_check[temp] = line_count
                elif l0.startswith("to "):
                   print("WARNING possible to-auxiliary l0 {} {}".format(line_count, l0.strip()))
                if (l0.startswith("this is the") or ("(this is the") in l0) and " rule" in l0:
                    if temp in auxil_check:
                        print("Duplicate rule", temp, line_count)
                    else:
                        auxil_check[temp] = line_count
    if current_table:
        print("End of file check")
        check_my_loop(current_table)

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'p':
        print_what_to_do = True
    elif arg == 'w':
        write_out = True
    elif arg == 'c':
        copy_back = True
    elif arg in ( 'pw', 'wp' ):
        print_what_to_do = write_out = True
    else:
        sys.exit("Bad parameter {}".format(arg))
    cmd_count += 1

if not my_proj and not default_proj:
    sys.exit("Go to a project directory, define a default project or specify one on the command line.")

current_table = ''

find_ignores()

if not files_with_tables[my_proj]:
    print("Going with default table file for project {}.".format(my_proj))
    files_with_tables[my_proj] = ['ta']
for x in files_with_tables[my_proj]:
    if print_what_to_do:
        print_dont_write(i7.header(my_proj, x))
    if write_out:
        write_dont_print(i7.header(my_proj, x))
for x in tables_to_check[my_proj]:
    if not tables_to_check[my_proj][x]:
        print("We did not see", x, "in", my_proj)

