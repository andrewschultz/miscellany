# bold.py
# looks for CAPITALIZED stuff inside quotes to put in BOLD with [b] [r] tags.
# ignore = actual bold text to ignore
# ignore_auxiliary = non bold case by case text that should be flagged as ignorable
#
# to-do (but very low priority):
#    track anything in more than one ignore_local
#    allow for custom ignoring in def bolded_caps based on project
#    allow for optional dashes or slashes in long string (dashes: done)
#    allow for leading articles e.g. [b]A MOTTO[r] instead of A [b]MOTTO[r] <- this is hard coded right now
#    one-offs: allow for a certain potentially suspicious word to get 1 or more than 1 tries, but flag it
#    fish for words in multiple project ignores to see if maybe they go in the general ignores

import mytools as mt
import sys
import i7
import re
import pyperclip
import os
from filecmp import cmp
import colorama

from collections import defaultdict

stderr_text = ''
file_includes = []
file_excludes = []
ignores = defaultdict(list)
ignore_auxiliary = defaultdict(list)
unignores = defaultdict(list)
counts = defaultdict(int)
bail_at = defaultdict(list)
unbail_at = defaultdict(list)
rule_ignore = defaultdict(list)

max_errors = 0
stderr_now = False
show_line_count = False
show_count = False
count = 0
clip = False
list_caps = False
write_comp_file = False
just_find_stuff = False
ignore_single_word_quote = True
bold_dashes = True
bold_commas = True
only_one = False
exact_find = False
find_copy_paste_stuff = False
italic_text_alt = True

test_array = []

what_to_find_string = "A-Z "

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

def special_mod(my_line):
    if ignore_single_word_quote:
        my_line = re.sub(r'"\[b\]([a-zA-Z]+)\[r\]"', r'"\1"', my_line)
    if italic_text_alt:
        if ('ital-say') in my_line:
            my_line = my_line.replace('[r][i]', '[i]').replace('[r]', '[i]')
    return my_line

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

def bold_cfg_array_of(my_data):
    dary = my_data.strip().split(',')
    for x in dary:
        if x.endswith('`'):
            print("WARNING match string cannot end with backtick/comma:", x)
        if x != x.strip():
            print("WARNING match string was stripped of end/start whitespace <{}>".format(x))
    return [x.replace('`', ',').replace('~', ',').strip() for x in dary]

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
            if prefix.lower() == 'projects':
                current_projs = bold_cfg_array_of(data)
                continue
            if prefix.lower() == 'bail':
                for cp in current_projs:
                    bail_at[cp].extend(bold_cfg_array_of(data))
                continue
            if prefix.lower() == 'unbail':
                for cp in current_projs:
                    unbail_at[cp].extend(bold_cfg_array_of(data))
                continue
            if prefix.lower() in ( 'project', 'proj' ):
                current_projs = bold_cfg_array_of(data)
                continue
            if prefix.lower() == 'ruleignore':
                rule_ignore[cp].append(data)
            if prefix.lower() == 'unignore':
                if 'global' in current_projs:
                    print("CANNOT HAVE UNIGNORE IN GLOBAL SECTION. It is for specific projects.")
                    continue
                for x in bold_cfg_array_of(data):
                    for cp in current_projs:
                        if x in unignores[cp]:
                            print("duplicate unignore {} at line {}, for project {}.".format(x, line_count, cp))
                            continue
                        unignore[cp].append(x)
                continue
            for x in bold_cfg_array_of(line):
                for cp in current_projs:
                    if x in ignores[cp] or x in ignore_auxiliary[cp]:
                        print("duplicate ignore {} at line {}, for project {}.".format(x, line_count, cp))
                        continue
                    if x == x.upper():
                        ignores[cp].append(x)
                    else:
                        ignore_auxiliary[cp].append(x)

def just_find(my_file, stuff_to_find):
    mfb = os.path.basename(my_file)
    search_string = r'(\b|\]){}{}'.format(stuff_to_find, r'\b' if exact_find else "")
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if re.search(search_string, line):
                print(mfb, line_count, line.rstrip())

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
    x = re.sub(r"(?<!(\[b\]))\b([A-Z] )*([A-Z]+[{}]*[A-Z])\b".format(what_to_find_string), lambda x: maybe_bold(x.group(0)), my_str)
    x = x.replace("[b][b]", "[b]")
    x = x.replace("[r][r]", "[r]")
    x = x.replace("[first custom style][b]", "[first custom style]") # ugh, this is a horrible hack, but for Shuffling/Roiling, we want to be able to keep red CAPS text ... we could allow for permissible_previous e.g. SA/[first custom style] but it is feature creep
    x = x.replace("[second custom style][b]", "[second custom style]") # ugh, this is a horrible hack, but for Shuffling, we want to be able to keep red CAPS text ... we could allow for permissible_previous e.g. SA/[first custom style] but it is feature creep
    x = x.replace("[bluetext][b]", "[bluetext]") # ugh, this is a horrible hack, but for Shuffling, we want to be able to keep red CAPS text ... we could allow for permissible_previous e.g. SA/[first custom style] but it is feature creep
    x = x.replace("[i][b]", "[i]") # this too ... but it happens in some cases ... we should maybe toggle this option?
    x = re.sub(r"(\[b\][ A-Z:']+)\[b\]", r'\1', x)
    return x

def code_exception(my_line):
    if "a-text" in my_line or "b-text" in my_line:
        return True
    if my_line.startswith("understand") and "as a mistake" not in my_line:
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

def bold_modify(my_line):
    by_quotes = my_line.split('"')
    new_ary = []
    for x in range(0, len(by_quotes)):
        if x % 2 == 0:
            new_ary.append(by_quotes[x])
        else:
            new_ary.append(bolded_caps(by_quotes[x]))
    new_quote = '"'.join(new_ary)
    return special_mod(new_quote)

def rule_ignorable(my_line):
    for r in rule_ignore[my_project]:
        if r in my_line:
            return True
    return False

def process_potential_bolds(my_file):
    count_err_lines = 0
    count_total_bolds = 0
    if write_comp_file:
        f = open(comp_file, "w", newline='')
    broken = False
    ignore_this_rule = False
    # sys.stderr.write("{} starting {}.\n".format('=' * 50, my_file))
    mfb = os.path.basename(my_file)
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if string_match(line, unbail_at):
                broken = False
            if broken or code_exception(line): # letters settler readings don't count
                if write_comp_file:
                    f.write(line)
                continue
            if not line.strip():
                ignore_this_rule = False
            if ignore_this_rule:
                continue
            if not line.startswith('\t'):
                if rule_ignorable(line):
                    ignore_whole_rule = True
                    continue
            if string_match(line, bail_at):
                broken = True
                if write_comp_file:
                    f.write(line)
                continue
            lr = line.rstrip()
            out_string = new_quote = bold_modify(lr)
            if new_quote != lr:
                if string_match(lr, ignore_auxiliary) or zap_nested_brax(new_quote) == zap_nested_brax(lr): # we ignore strings we acknowledge are ok, as well as stuff inside an IF statement
                    if write_comp_file:
                        f.write(line)
                    continue
                count_err_lines += 1
                count_total_bolds += new_quote.count('[b]') - lr.count('[b]')
                out_string = zap_nested_brax(out_string)
                if show_line_count:
                    out_string = "{} {}".format(line_count, new_quote)
                if show_count:
                    out_string = "{} {}".format(count_err_lines, new_quote)
                if max_errors and count_err_lines > max_errors:
                    if count_err_lines == max_errors + 1:
                        print("Reached maximum errors. Adjust with m#.")
                    out_string = lr.rstrip()
                else:
                    print(out_string)
            if write_comp_file:
                f.write(out_string + "\n")
    this_stderr_text = "{} {} has {} total bold line candidates, {} total bold word/phrase candidates.\n".format('=' * 50, mfb, count_err_lines, count_total_bolds)
    if stderr_now:
        sys.stderr.write(this_stderr_text)
    else:
        global stderr_text
        stderr_text += this_stderr_text
    if write_comp_file:
        f.close()
        if count_err_lines == 0:
            if not cmp(my_file, comp_file):
                print("Newline differences between {} and {}.".format(mfb, comp_file))
            return
        print("Line/bold-text differences:", count_err_lines, count_total_bolds)
        mt.wm(my_file, comp_file)
    if only_one and count_err_lines:
        print("Bailing after first file difference.")
        if not stderr_now:
            sys.stderr.write(this_stderr_text)
        sys.exit()

cmd_count = 1

while cmd_count < len(sys.argv):
    (arg, val, found_val) = mt.parnum(sys.argv[cmd_count])
    argraw = sys.argv[cmd_count]
    if argraw == 'o1':
        only_one = True
    elif arg == 'c':
        clip = True
    elif arg == 'l':
        list_caps = True
    elif arg in ( 'ia', 'ai' ):
        italic_text_alt = True
    elif mt.alpha_match(arg, 'ain'):
        italic_text_alt = False
    elif arg == 'l':
        list_caps = True
    elif arg == 'cp':
        find_copy_paste_stuff = True
    elif arg == 't' and found_val:
        f = open("c:/writing/scripts/bold-test-{}.txt")
        test_array_extend([x for x in f.readlines() if x and not x.startswith('#') and not x.startswith(';')])
    elif arg == 'es':
        mt.npo(main.__file__)
    elif arg in ( 'ec', 'ed', 'ei', 'ce', 'de', 'ie' ):
        mt.npo(bold_ignores)
    elif arg in ( 'dn', 'nd' ):
        bold_dashes = False
    elif arg in ( 'dy', 'yd' ):
        bold_dashes = True
    elif arg in ( 'bcn', 'nbc' ):
        bold_commas = False
    elif arg in ( 'bcy', 'ybc' ):
        bold_commas = True
    elif arg in ( 'sn', 'ns' ):
        stderr_now = True
    elif arg in ( 'sl', 'ls' ):
        stderr_now = False
    elif mt.alpha_match(arg, 'isw'):
        ignore_single_word = True
    elif mt.alpha_match(arg, 'nisw'):
        ignore_single_word = False
    elif arg[:2] in ( 'j:', 'j=' ):
        just_find_stuff = True
        exact_find = True
        find_string = '|'.join(arg[2:].upper().split(','))
    elif arg[:3] in ( 'ja:', 'ja=' ):
        just_find_stuff = True
        exact_find = False
        find_string = '|'.join(arg[3:].upper().split(','))
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

if bold_commas:
    what_to_find_string += ','
if bold_dashes:
    what_to_find_string += '-'

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
    sys.exit()

get_ignores()
if find_copy_paste_stuff:
    cp = pyperclip.paste()
    test_array = [x for x in cp.split("\n") if x]

if len(test_array):
    test_array = list(dict.fromkeys(test_array))
    for this_line in test_array:
        if not this_line:
            continue
        temp = bold_modify(this_line)
        print(this_line)
        if temp == this_line:
            print("IDENTICAL")
        else:
            print(temp)
    sys.exit()

for x in i7.i7f[my_project]:
    if len(file_includes) and not in_match(x, file_includes):
        continue
    if len(file_excludes) and in_match(x, file_excludes):
        continue
    if just_find_stuff:
        just_find(x, find_string)
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

if write_comp_file and os.path.exists(comp_file):
    os.remove(comp_file)
