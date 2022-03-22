# bold.py
# looks for CAPITALIZED stuff inside quotes to put in BOLD with [b] [r] tags.
# ignore = actual bold text to ignore
# ignore_auxiliary = non bold case by case text that should be flagged as ignorable

import mytools as mt
import sys
import i7
import re
import pyperclip
import os
from filecmp import cmp

from collections import defaultdict

stderr_text = ''
file_includes = []
file_excludes = []
ignores = defaultdict(list)
ignore_auxiliary = defaultdict(list)
unignores = defaultdict(list)
counts = defaultdict(int)
bail_at = defaultdict(list)

max_errors = 0
stderr_now = False
show_line_count = False
show_count = False
count = 0
clip = False
list_caps = False
write_comp_file = False

bold_ignores = "c:/writing/scripts/boldi.txt"
comp_file = "c:/writing/temp/bold-py-temp-file.txt"

def usage(header = '==== GENERAL USAGE ===='):
    print("c = clipboard(deprecated)")
    print("l = list caps")
    print("sl / ls = stderr text later, sn / ns = stderr text now")
    print("w = write temp compare file and open in WinMerge")
    print("f+ f= are file wildcards to include, f- are file wildcards to exclude, w instead of f writes to temp compare")
    print("es = open source, ec/ed/ei = open cfg/data file")
    sys.exit()

def zap_nested_brax(my_string):
    brax_depth = 0
    out_string = ''
    for x in range(0, len(my_string)):
        if my_string[x] == '[':
            brax_depth += 1
        if brax_depth < 2:
            out_string += my_string[x]
        if my_string[x] == ']':
            brax_depth -= 1
    return out_string

def get_ignores():
    if not os.path.exists(bold_ignores):
        print("No ignores file {}.".format(bold_ignores))
        return
    current_projs = ["global"]
    with open(bold_ignores) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"):
                continue
            if line.startswith(";"):
                break
            (prefix, data) = mt.cfg_data_split(line)
            if prefix.lower() == 'bail':
                for cp in current_projs:
                    bail_at[cp].extend(data.split(','))
                continue
            if prefix.lower() in ( 'project', 'proj' ):
                cur_projs = data.split(',')
                continue
            if prefix.lower == 'unignore':
                if 'global' in cur_projs:
                    print("CANNOT HAVE UNIGNORE IN GLOBAL SECTION. It is for specific projects.")
                    continue
                for x in line.strip().split(','):
                    for cp in current_projs:
                        if x in unignores[cp]:
                            print("duplicate unignore {} at line {}, for project {}.".format(x, line_count, cp))
                            continue
                        unignore[cp].append(x)
                continue
            for x in line.strip().split(','):
                for cp in current_projs:
                    if x in ignores[cp] or x in ignore_auxiliary[cp]:
                        print("duplicate ignore {} at line {}, for project {}.".format(x, line_count, cp))
                        continue
                    if x == x.upper():
                        ignores[cp].append(x)
                    else:
                        ignore_auxiliary[cp].append(x)

def maybe_bold(my_str):
    if my_str.count(' ') > 2:
        return my_str
    if re.search("^[RYGPB\*\?]{3,}$", my_str):
        return my_str
    if my_str in ignores[my_project] or my_str in ignores['global'] and my_str not in unignores[my_project]:
        return my_str
    counts[my_str] += 1
    return '[b]{}[r]'.format(my_str)

def bolded_caps(my_str):
    x = re.sub(r"(?<!(\[b\]))\b([A-Z]{2,}[A-Z ]*[A-Z])\b", lambda x: maybe_bold(x.group(0)), my_str)
    x = x.replace("[b][b]", "[b]")
    x = x.replace("[r][r]", "[r]")
    x = re.sub(r"(\[b\][ A-Z:']+)\[b\]", r'\1', x)
    return x

def code_exception(my_line):
    if "a-text" in my_line or "b-text" in my_line or my_line.startswith("understand"):
        return True
    return False

def in_match(my_string, my_list, case_sensitive = False):
    for x in my_list:
        if case_sensitive:
            if x in my_string:
                return True
        elif x.lower() in my_string.lower():
            return True
    return False

def string_match(my_line, my_dict):
    for ia in my_dict[my_project]:
        if ia in my_line:
            return True
    for ia in my_dict['global']:
        if ia in my_line:
            return True
    return False

def process_potential_bolds(my_file):
    count = 0
    if write_comp_file:
        f = open(comp_file, "w", newline='')
    broken = False
    # sys.stderr.write("{} starting {}.\n".format('=' * 50, my_file))
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if broken or code_exception(line): # letters settler readings don't count
                if write_comp_file:
                    f.write(line)
                continue
            if string_match(line, bail_at):
                broken = True
                if write_comp_file:
                    f.write(line)
                continue
            lr = line.rstrip()
            by_quotes = lr.split('"')
            new_ary = []
            for x in range(0, len(by_quotes)):
                if x % 2 == 0:
                    new_ary.append(by_quotes[x])
                else:
                    new_ary.append(bolded_caps(by_quotes[x]))
            new_quote = '"'.join(new_ary)
            out_string = new_quote
            if new_quote != lr:
                if string_match(lr, ignore_auxiliary) or zap_nested_brax(new_quote) == zap_nested_brax(lr): # we ignore strings we acknowledge are ok, as well as stuff inside an IF statement
                    if write_comp_file:
                        f.write(line)
                    continue
                count += 1
                if show_line_count:
                    out_string = "{} {}".format(line_count, new_quote)
                if show_count:
                    out_string = "{} {}".format(count, new_quote)
                if max_errors and count > max_errors:
                    if count == max_errors + 1:
                        print("Reached maximum errors. Adjust with m#.")
                    out_string = lr.rstrip()
                else:
                    print(out_string)
            if write_comp_file:
                f.write(out_string + "\n")
    this_stderr_text = "{} {} has {} total boldable lines.\n".format('=' * 50, my_file, count)
    if stderr_now:
        sys.stderr.write(this_stderr_text)
    else:
        global stderr_text
        stderr_text += this_stderr_text
    if write_comp_file:
        f.close()
        if count == 0:
            if not cmp(my_file, comp_file):
                print("Newline differences between {} and {}.".format(my_file, comp_file))
            return
        print("Total differences:", count)
        mt.wm(my_file, comp_file)

cmd_count = 1

while cmd_count < len(sys.argv):
    (arg, val, found_val) = mt.parnum(sys.argv[cmd_count])
    if arg == 'c':
        clip = True
    elif arg == 'l':
        list_caps = True
    elif arg == 'es':
        mt.npo(main.__file__)
    elif arg in ( 'ec', 'ed', 'ei' ):
        mt.npo(bold_ignores)
    elif arg in ( 'sn', 'ns' ):
        stderr_now = True
    elif arg in ( 'sl', 'ls' ):
        stderr_now = False
    elif arg == 'm':
        if not found_val:
            sys.exit("Need value after m.")
        max_errors = val
    elif arg == 'w':
        write_comp_file = True
    elif arg[:2] in ( 'w+', 'w=' ):
        file_includes = arg[2:].split(',')
        write_comp_file = True
    elif arg.startswith( 'w-' ):
        file_excludes = arg[2:].split(',')
        write_comp_file = True
    elif arg[:2] in ( 'f+', 'f=' ):
        file_includes = arg[2:].split(',')
    elif arg.startswith( 'f-' ):
        file_excludes = arg[2:].split(',')
    else:
        usage()
    cmd_count += 1

if len(file_includes) and len(file_excludes):
    sys.exit("You can only have one of w+ and w- to include or exclude files.")

my_project = i7.dir2proj()

if not my_project:
    sys.exit("You need to go to a directory with a project.")

if clip:
    print("NOTE: CLIP deprecated for bold.py | clip")
    orig = pyperclip.paste()
    final = bolded_caps(orig)
    print(final)
else:
    get_ignores()
    for x in i7.i7f[my_project]:
        if len(file_includes) and not in_match(x, file_includes):
            continue
        if len(file_excludes) and in_match(x, file_excludes):
            continue
        process_potential_bolds(x)

if list_caps:
    counts_list = sorted(list(counts))
    print("#{} total ignores".format(len(counts_list)))
    while len(counts_list) > 0:
        print("#{}".format(','.join(["{}={}".format(x, counts[x]) for x in counts_list[:10]])))
        counts_list = counts_list[10:]

if stderr_text:
    print(stderr_text)

if write_comp_file:
    os.remove(comp_file)
