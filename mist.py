# mist.py
#
# mistake file/script tracker/aligner
#
# mist-d.txt has default messages for projects for error testing
#

import i7
import os
import re
import sys
import glob
import pyperclip
import mytools as mt

from collections import defaultdict

# ary = ['roiling', 'shuffling']
# ary = ['shuffling']
ary = []
projs = []


added = defaultdict(bool)
srev = defaultdict(str)
condition = defaultdict(str)
location = defaultdict(str)

base_err = defaultdict(str)

end_room = ""

short = { 'shuffling':'sa', 'roiling':'roi', 'ailihphilia':'ail' }

#unusued, but if something is not the default_room_level, it goes here.
default_room_level = 'chapter'
levs = { }

clipboard_str = ""

mistake_defaults = "c:/writing/scripts/mist-d.txt"

for x in short: srev[short[x]] = x

def usage():
    print("All commands can be with or without hyphen")
    print("-f# = max # of missing mistake tests to find")
    print("-a/-na = check stuff afte or don't")
    print("-b = minimum brackets to flag (number right after b), -nb disables this")
    print("-w/-nw = write or don't")
    print("-c/-nc = write conditions or don't")
    print("-l/-nl = write locations or don't")
    print("-2 = to clipboard")
    print("-p/-np = print or don't")
    print("-po/-wo = print or write only")
    print("-e = edit the data file, -ec/ce = edit source, -eb = edit branches")
    print("Other arguments are the project name, short or long")
    exit()

def read_from_mist_data(mist_data):
    f = defaultdict(list)
    sf = defaultdict(list)
    with open(mist_data) as file:
        for (line_count, line) in enumerate(file, 1):
            line = line.lower().strip()
            if line.startswith("#"): continue
            if line.startswith(";"): break
            to_sf = False
            if line[:6] == 'small:':
                line = line[6:]
                to_sf = True
            ary = line.split("=")
            if to_sf:
                sf[ary[0]].extend(ary[1].split(','))
            else:
                f[ary[0]].extend(ary[1].split(','))
    return (f, sf)

def bad_brackets(my_line):
    if my_line.startswith("#"): return False
    if my_line.count("[") != my_line.count("]"): return True
    if my_line.count("[") > bracket_minimum: return True
    if my_line.startswith("[") and my_line.endswith("."): return True
    if "[']" in my_line: return True

def mistake_msg(proj):
    if proj in base_err.keys(): return base_err[proj]
    return "(Need default for project {:s} in {:s}) That's not something you can do or say here.".format(proj, mistake_defaults)

def clip_out(x):
    if print_output: print(x)
    global clipboard_str
    if to_clipboard: clipboard_str += x + "\n"
    return

def to_full(a):
    if a in srev.keys(): return srev[a]
    if a in short.keys(): return a
    print(a, "not a project with a recognized mistake file.")
    exit()

def read_mistake_defaults():
    with open(mistake_defaults) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(";"): break
            if line.startswith("#"): continue
            l0 = "\t".split(line.lower().strip())
            if len(l0) != 2: sys.exit("Need a tab separating project and default message at line {:d}.".format(line_count))
            base_err[l0[0]] = l0[1]

def mister(a, my_file, do_standard):
    global clipboard_str
    check_this_after = check_stuff_after and do_standard
    to_look = files[a] if do_standard else smallfiles[a]
    mistakes = 0
    flags = 0
    bracket_errs = 0
    duplicates = 0
    superfluous = 0
    help_text_rm = 0
    need_comment = 0
    need_test = defaultdict(int)
    mistake_text = defaultdict(str)
    cmd_text = defaultdict(str)
    found = defaultdict(bool)
    comment_found = defaultdict(bool)
    comment_line = defaultdict(int)
    comment_file = defaultdict(str)
    full_line = defaultdict(str)
    source_dir = "c:/games/inform/{:s}.inform/Source/".format(a)
    count = 0
    special_def = ''
    room_sect_var = default_room_level if a not in levs.keys() else levs[a]
    last_loc = '(none)'
    slashes = []
    mults = []
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            l = line.strip()
            if line.startswith(room_sect_var):
                last_loc = re.sub(r'^[a-z]+ +', '', line.strip().lower())
            elif line.startswith("book"):
                last_loc = re.sub(r'^book +', 'REGION ', line.strip().lower())
            if l.startswith("[def="):
                special_def = re.sub("^\[def=", "", l)
                special_def = re.sub("\].*", "", special_def)
                continue
            if re.search("understand.*as a mistake", l, re.IGNORECASE) and not l.startswith('['):
                cmd = re.sub("understand +\"", "", l)
                cmd = re.sub("\" as a mistake.*", "", cmd)
                cmd = re.sub("\"", "", cmd)
                cmd = re.sub(" and ", "/", cmd)
                if special_def != '':
                    x = special_def
                else:
                    x = cmd
                # print("OK,", x)
                x = x.lower()
                cmd_text[x] = cmd
                mistake_text[x] = re.sub(".*\(\"", "", l)
                mistake_text[x] = re.sub("\"\).*", "", mistake_text[x])
                mistake_text[x] = re.sub("\[mis of [0-9]+\]", "", mistake_text[x])
                if x in need_test.keys() and '[okdup]' not in l.lower():
                    print('Uh oh,', x, 'duplicates line', need_test[x], 'at line', line_count, 'in', os.path.basename(my_file))
                need_test[x] = line_count
                full_line[x] = line.strip()
                found[x] = False
                comment_found[x] = False
                if 'when' in l.lower():
                    condition[x] = re.sub(".*when *", "", l.lower())
                else:
                    condition[x] = 'ALWAYS (unless there\'s a bug here)'
                location[x] = last_loc
            special_def = ''
    # for p in sorted(need_test.keys(), key=need_test.get):
        # print(p, need_test[p])
    # files = glob.glob(source_dir + "reg-" + short[a] + "-thru*.txt")
    extra_text = defaultdict(str)
    ignore_next = False
    for fi in to_look:
        short_fi = os.path.basename(fi)
        retest = False
        fs = os.path.basename(fi)
        with open(fi) as file:
            err_count = 0
            test_note = ""
            for (line_count, line) in enumerate(file, 1):
                if ignore_next == True:
                    ignore_next = False
                    # print ("Purposely ignored command -- probably a point scorer before you need to ignore it, line_count, line.strip())
                    continue
                if retest == True:
                    retest = False
                    # print("Skipping", line.strip())
                    continue
                if line.startswith("#not a mistake") or (line.startswith("#pre-") and " rule" in line):
                    ignore_next = True
                    continue
                if line.startswith("#mistake retest"):
                    test_note = re.sub("^#mistake retest( for)? ", "", line.strip().lower())
                    if test_note not in comment_found.keys():
                        print("Retest of errant test case {} at {} line {}.".format(test_note, short_fi, line_count))
                    elif not comment_found[test_note]:
                        print("Retest occurs before test {} at {} line {}.".format(test_note, short_fi, line_count))
                    retest = True
                    continue
                if line.startswith("#mistake text") or line.startswith("#mistake retext"):
                    print('Line {} says text not test (X not S).'.format(line_count))
                    continue
                if line.startswith("##mistake"):
                    print('Line {} has one two many pound signs.'.format(line_count))
                    continue
                if line.startswith('#') and 'to find' in line:
                    print('Line {} comment mentions search info: {}'.format(line_count, line.strip().lower()))
                if line.startswith("##condition(s)") or line.startswith("##location"):
                    print('Line {} has helper text to remove: {}'.format(line_count, line.strip().lower()))
                    help_text_rm += 1
                brax = line.count('[')
                if bad_brackets(line):
                    print(brax, 'floating ' + ('if' if '[if' in line else 'code') + '-brackets in line', line_count, 'of', short_fi, ':', line.strip().lower())
                    bracket_errs += 1
                    if to_clipboard:
                        clipboard_str += re.sub("mistake test", "mistake retest", last_mistake) + last_cmd + line + '\n'
                retest = False
                if line.startswith("#mistake "):
                    last_mistake = line
                    test_note = re.sub("^#mistake test for ", "", line.strip().lower())
                    if test_note not in comment_found.keys():
                        print('Superfluous(?) mistake test', test_note, 'at line', line_count, 'of', short_fi)
                        if '/' in test_note:
                            slashes.append(test_note)
                        superfluous += 1
                    else:
                        if comment_found[test_note]:
                            if comment_file[test_note] == fs:
                                print('Duplicate mistake test for', test_note, 'at line', line_count, fs, 'original', comment_line[test_note], 'Delta=', line_count - comment_line[test_note], '(reroute to mistake retest?)')
                            else:
                                print('Duplicate mistake test for', test_note, 'at line', line_count, fs, 'original', comment_line[test_note], 'File', comment_file[test_note], '(reroute to mistake retest?)')
                            duplicates += 1
                        else:
                            comment_found[test_note] = True
                            comment_line[test_note] = line_count
                            comment_file[test_note] = fs
                        err_count += 1
                        # print("Got", test_note)
                elif line.startswith('>'):
                    last_cmd = line
                    ll = re.sub("^>", "", line.strip().lower())
                    if test_note and test_note in found.keys():
                        found[test_note] = True
                        continue
                    if ll != test_note:
                        if ll in need_test.keys():
                            if found[ll] is False:
                                err_count += 1
                                if print_output:
                                    print("({:4d}) {:14s} Line {:4d} #not a mistake/#mistake test (or define [def=special test]) for {:s}".format(err_count, fi, line_count, ll))
                                    print("    ", full_line[ll])
                                need_comment += 1
                            extra_text[line_count] = ll
                            found[ll] = True
                    ll = ""
                    test_note = ""
                else:
                    ll = ""
                    test_note = ""
        if write_file:
            out_file = source_dir + "pro-" + short_fi
            fout = open(out_file, "w")
            print("Writing", out_file)
            mistakes_added = 0
            with open(fi) as file:
                count = 0
                for line in file:
                    count += 1
                    if count in extra_text.keys():
                        if end_room and end_room in location[count]: break
                        fout.write("##mistake test for " + extra_text[count] + "\n")
                        if print_location: fout.write("##location = " + location[count])
                        if print_condition: fout.write("##condition(s) " + condition[count])
                        mistakes_added += 1
                    fout.write(line)
            fout.close()
            print(mistakes_added, "total mistakes added.")
    find_count = 0
    check_after = defaultdict(int)
    for f in sorted(found.keys(), key=need_test.get):
        if found[f] == False:
            find_count += 1
            ctf = cmd_text[f].split('/')
            for ct in ctf:
                check_after[ct] = len(ctf)
            if print_output or to_clipboard:
                if (find_max == 0 or find_count <= find_max) and find_count > find_min:
                    if end_room and end_room in location[f]: break
                    if print_output:
                        if verbose:
                            print('#mistake test for {:80s}{:4d} to find({:d})'.format(f, find_count, need_test[f]))
                        else:
                            print('#{:4d} to find({:d})'.format(find_count, need_test[f]))
                    if print_location and print_output: print("##location =", location[f])
                    if print_condition and print_output: print("##condition(s)", condition[f])
                    clip_out("#mistake test for {:s}".format(f))
                    for ct in cmd_text[f].split('/'):
                        clip_out(">{:s}".format(re.sub("\[text\]", "zozimus", ct)))
                        clip_out(mistake_text[f] if do_standard else mistake_msg(a))
                    if to_clipboard: clipboard_str += "\n"
                    mistakes += 1
                    if print_output: print()
    if check_this_after:
        regs = [re.sub(r'\\', '/', x.lower()) for x in glob.glob(source_dir + "reg-*.txt")]
        check_ary = ['>' + x for x in sorted(check_after.keys())]
        files_to_check = defaultdict(bool)
        for f2 in files[a]:
            files_to_check[f2] = True
        for f1 in regs:
            with open(f1) as file:
                for (line_count, line) in enumerate(file, 1):
                    if not line.startswith('>'): continue
                    for c in check_ary:
                        if line.strip() == c:
                            c1 = c[1:] if c.startswith('>') else c
                            if check_after[c1] > 1:
                                mults.append(c1)
                            print(f1, line_count, c, ("may be false flagged" if f1 in files_to_check.keys() else "could be transferred to main files or may be part of a mistyped combo of mistake commands."))
                            flags += 1
        if len(slashes):
            print("Combo-mistakes that don't work:")
            print("\n".join(slashes))
        if len(mults):
            print("Combo-mults possibly false flagged:")
            print("/".join(mults))
    if not (mistakes + flags + duplicates + superfluous + bracket_errs + help_text_rm + need_comment):
        print("No errors found for {:s}!".format(a))
    else:
        totes = mistakes + flags + duplicates + superfluous + bracket_errs + help_text_rm + need_comment
        print(a, mistakes, "mistakes,", flags, "flags", duplicates, "duplicates", superfluous, "superfluous", bracket_errs, "brackets", help_text_rm, "helper text", need_comment, "need comment", totes, "total")

files = defaultdict(str)
smallfiles = defaultdict(str)
mist_data = "c:/writing/scripts/mist.txt"
(files, smallfiles) = read_from_mist_data(mist_data)

edit_data = False
edit_branches = False
edit_source = False
run_check = False
to_clipboard = False
write_file = False
print_output = True
verbose = False
print_condition = True
print_location = True
check_stuff_after = True
find_max = 0
find_min = 0
bracket_minimum = 1
bracket_check = True
clipboard_str = ''

if len(sys.argv) > 1:
    count = 1
    while count < len(sys.argv):
        arg = sys.argv[count].lower()
        if arg[0] == '-': arg = arg[1:]
        if arg == 'w': write_file = True
        elif arg == 'nw': write_file = False
        elif arg == '2': to_clipboard = True
        elif arg == '2o' or arg == '20':
            to_clipboard = True
            print_output = False
        elif arg[:2] == 'fm': find_min = int(arg[2:])
        elif arg[0] == 'f': find_max = int(arg[1:])
        elif arg == 'e': edit_data = True
        elif arg == 'eo' or arg == 'oe': edit_data_only = True
        elif arg == 'eb' or arg == 'be':
            edit_branches = True
        elif arg == 'ec' or arg == 'ce':
            edit_source = True
            run_check = False
        elif arg == 'a': check_stuff_after = True
        elif arg == 'na': check_stuff_after = False
        elif arg == 'b':
            bracket_minimum = int(arg[1:])
            if bracket_minimum < 1:
                print("Must have bracket minimum over 1. Ignoring brackets")
                bracket_check = False
        elif arg == 'nb': bracket_check = False
        elif arg == 'c': print_condition = True
        elif arg == 'nc': print_condition = False
        elif arg == 'c': print_location = True
        elif arg == 'nc': print_location = False
        elif arg == 'wo':
            write_file = True
            print_output = False
        elif arg == 'np': print_output = False
        elif arg == 'p': print_output = True
        elif arg == 'po':
            print_output = True
            write_file = False
        elif arg[:2] == 'e=':
            end_room = arg[2:].replace("-", " ")
        elif arg == '?': usage()
        else:
            for q in arg.split(','):
                if q in added.keys():
                    print(q, "already in.")
                elif q in short.keys():
                    print("Adding", q)
                    added[q] = True
                elif q in i7.i7x.keys() and i7.i7x[q] in short.keys():
                    print("Adding", i7.i7x[q])
                    added[i7.i7x[q]] = True
                else:
                    print(q, "not recognized as a project with a mistake file and/or regex test files.")
                    print('=' * 50)
                    usage()
        count += 1

if edit_source:
    mt.open_source()

if edit_data:
    i7.npo(mist_data)

if not write_file and not print_output and not to_clipboard:
    print("You need to write a file or the clipboard or print the output.")
    exit()

if len(added.keys()) == 0:
    x = i7.dir2proj(os.getcwd())
    if x in short.keys():
        print("Going with default", x)
        added[x] = True
    else:
        print("No mistake file in default directory.")

if edit_branches:
    for a in added.keys():
        for b in files[a]:
            i7.npo(b, True, bail=False)
    if len(added): exit()
    if not run_check: exit()

for e in sorted(added.keys()):
    mist_file = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/{:s} mistakes.i7x".format(e)
    if e in smallfiles.keys():
        print(e, "smallfile check:", ', '.join(smallfiles[e]))
        mister(e, mist_file, False)
    print(e, "regular file check:", os.path.basename(mist_file))
    mister(e, mist_file, True)

if clipboard_str:
    pyperclip.copy(clipboard_str)
    pyperclip.paste()
    lines = len(clipboard_str.split("\n"))
    print("Rough testing text sent to clipboard,", lines, "lines.")
