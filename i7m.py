from collections import defaultdict
from shutil import copyfile
import os
import re
import argparse

big_string = ""
iffy = False

next_break_over = False
went_over = False
else_next_bad = False

file_name = "story.ni"

copy_over = False
save_copy = False
launch_win_diff = False
unix_endings = True
collapse_to_one_line = False
trivial_punctuation = False
cut_off_immediately = False

this_tabs = 0
last_tabs = 0

max_fix_line = 0
min_fix_line = 0

last_num = 0

max_changes = 25
cur_changes = 0

trivial_punctuation = 0

max_collapse = 0
func_collapse = 0

func_name = ''

def leading_tabs(l):
    return len(l) - len(l.lstrip('\t'))

file_hash = defaultdict(str)

with open("c:/writing/scripts/i7m.txt") as file:
    for line in file:
        assign = line.strip().split("\t")
        if file_hash[assign[0]]:
            print(assign[0], 'shortcut already', file_hash[assign[0]], 'reassigned', assign[1])
        file_hash[assign[0]] = assign[1]

parser = argparse.ArgumentParser(description='semicolon to comma.', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-m', '--max_change_num', action='store', dest='max_changes', help='maximum changes', type=int)
parser.add_argument('-maxl', '--max_change_line', action='store', dest='max_fix_line', help='maximum line', type=int)
parser.add_argument('-minl', '--min_change_line', action='store', dest='min_fix_line', help='minimum line', type=int)
parser.add_argument('-mc', '--max_collapse', action='store', dest='max_collapse', help='maximum collapses', type=int)
parser.add_argument('-l', '--launchwindiff', action='store_true', dest='launch_win_diff', help='launch win diff')
parser.add_argument('-1', '--oneline', action='store_true', dest='collapse_to_one_line', help='one line functions remove tabs')
parser.add_argument('-c', '--copyover', action='store_true', dest='copy_over', help='copy generated file back over')
parser.add_argument('-t', '--trivpunc', action='store_true', dest='trivial_punctuation', help='fix trivial punctuation')
parser.add_argument('-cs', '--copysave', action='store_true', dest='copy_save', help='copy generated file back over and save')
parser.add_argument('-s', '--save', action='store_true', dest='save_after', help='save generated file')
parser.add_argument('-f', '--filename', action='store', dest='file_name', help='file name')
parser.add_argument('-fu', '--funcname', action='store', dest='func_name', help='func name', type=str)
parser.add_argument('-w', '--windows', action='store', dest='windows_endings', help='windows endings')
parser.add_argument('-a', '--abbrev', action='store', dest='file_abbrev', help='file hash abbreviation')
args = parser.parse_args()

if args.file_name:
    file_name = args.file_name
    if not os.path.exists(file_name):
        print("No such file", file_name, "so searching for hash (use -a instead next time).")
        if file_name in file_hash.keys():
            args.file_abbrev = args.file_name
        else:
            print("No hash found. Bailing.")
            exit()

if args.file_abbrev:
    if args.file_abbrev in file_hash.keys():
        file_name = file_hash[args.file_abbrev]
        print("Pulling hash name of", args.file_abbrev, ':', file_name)
    else:
        poss_array = []
        for x in file_hash.keys():
            if args.file_abbrev in x:
                poss_array.append(x)
        if len(poss_array) == 0:
            print("Invalid file hash. Available=", ', '.join(sorted(poss_array)))
            exit()
        elif len(poss_array) > 1:
            print("Too many possibilities:", ', '.join(poss_array))
            exit()
        else:
            print("Going with", poss_array[0], "as file hash.")
            file_name = file_hash[poss_array[0]]

if args.max_changes:
    max_changes = args.max_changes

if args.trivial_punctuation:
    trivial_punctuation = args.trivial_punctuation

if args.collapse_to_one_line:
    collapse_to_one_line = args.collapse_to_one_line

if args.launch_win_diff:
    launch_win_diff = True

if args.func_name:
    func_name = args.func_name

if args.windows_endings:
    unix_endings = False

if args.max_fix_line:
    max_fix_line = args.max_fix_line

if args.min_fix_line:
    min_fix_line = args.min_fix_line

if args.copy_over is True:
    copy_over = True
    copy_save = False

if args.copy_save is True:
    copy_save = True
    copy_over = True

if args.copy_save and args.copy_over:
    print("Conflicting options -c and -cs. -cs overrides.")

if args.copy_save and args.save_after:
    print("Conflicting options -s and -cs. -cs overrides.")

count = 0

in_i6 = False
func_begun = False
func_ended = False

with open(file_name) as file:
    for line in file:
        count += 1
        if next_break_over and not re.search("[a-z]", line, re.IGNORECASE):
            last_num = count - 1
            went_over = True
            next_break_over = False
        if func_name:
            if func_ended or not func_begun:
                if line.startswith(func_name):
                    print("Started reading function", func_name, "at", count)
                    func_begun = True
                else:
                    big_string = big_string + line
                    continue
            elif func_begun and line.strip() == '':
                big_string = big_string + line
                func_ended = True
                continue
        if re.search("\(-", line):
            in_i6 = True
        if re.search("-\)", line):
            in_i6 = False
        if trivial_punctuation and not in_i6 and re.search("^[a-z].*;$", line, re.IGNORECASE):
            # print(count," trivial punctuation change:", line)
            line = re.sub(";$", ".", line)
            trivial_punctuation += 1
        if count < min_fix_line:
            big_string = big_string + line
            continue
        if max_fix_line > 0 and count > max_fix_line and not iffy:
            big_string = big_string + line
            continue
        if went_over:
            big_string = big_string + line
            continue
        if else_next_bad and re.search("else:", line):
            cur_tabs = leading_tabs(line)
            if cur_tabs == this_tabs - 1:
                print("WARNING line", count, " (would be {:d})".format(count - cur_changes), "has extraneous else, tab compare this", cur_tabs, "that", this_tabs)
        else_next_bad = False
        if iffy:
            this_tabs = leading_tabs(line)
            if (re.search("\t(decide |no;|decide |decide |yes;|continue the action|the rule succeeds)", line) or re.search("\t.*instead;( \[.*\])?", line)) and not re.search("\t(if|unless) ", line) and (this_tabs - last_tabs == 1):
                l2 = re.sub("^\t+", "", line).strip()
                last_line = re.sub(":+", ", " + l2, last_line)
                big_string = big_string + last_line
                cur_changes += 1
                if cur_changes == max_changes and not cut_off_immediately:
                    next_break_over = True
                else_next_bad = True
                any_changes_yet = True
            elif (this_tabs - last_tabs == 1) and re.search("\t(if|unless) ", line):
                big_string = big_string + last_line
                last_line = line
                last_tabs = leading_tabs(line)
                iffy = True
                continue
            else:
                big_string = big_string + last_line + line
            iffy = False
            continue
        iffy = False
        last_line = line
#        if re.search("if action is iffy", line):
        if re.search("^\t+if ", line) and not re.search("(decide on [a-z0-9-]+|decide no|decide yes|instead)[;\.]", line) and ", case insensitively" not in line:
            if cur_changes < max_changes or next_break_over:
                iffy = True
                last_tabs = leading_tabs(line)
                continue
            elif cur_changes >= max_changes:
                last_num = count
        big_string = big_string + line

if func_begun is False and func_name:
    print("Could not find function", func_begun)
    exit()

if collapse_to_one_line:
    xxx = big_string.split("\n")
    xxx2 = []
    x = 0
    while x < len(xxx):
        xxx2.append(xxx[x])
        if xxx[x] == '' and x < len(xxx) - 2:
            if re.search("^[a-zA-Z]", xxx[x+1], re.IGNORECASE):
                if re.search("^\t[a-zA-Z]", xxx[x+2], re.IGNORECASE):
                    if xxx[x+3] == '' and (max_collapse == 0 or func_collapse < max_collapse):
                        comments = ''
                        if re.search("\[.*\]", xxx[x+1]):
                            print('line', x, 'has a comment:', xxx[x+1])
                            comments = re.sub(".*\[", " [", xxx[x+1])
                            xxx[x+1] = re.sub(" \[.*\]", "", xxx[x+1])
                        xxx[x+2] = re.sub(";$", ".", xxx[x+2])
                        new_string = xxx[x+1] + re.sub("^\t", " ", xxx[x+2]) + comments
                        x = x + 3
                        xxx2.append(new_string)
                        func_collapse += 1
                        continue
        x += 1
        continue
    print(func_collapse, "collapsed functions.")
    big_string = '\n'.join(xxx2)

if cur_changes == 0 and func_collapse == 0 and trivial_punctuation == 0:
    print("Nothing changed, so I'm not doing anything.")

# if unix_endings is false, then we want to get rid of the unix_endings and only have CR. Or is it LF? Whichever, we want to strip the ^M so Inform doesn't read it

if unix_endings:
    big_string.replace("\r\n", "\n")

if went_over is True:
    print(cur_changes, "total cur_changes, ended at line", last_num, "of", count)

if max_changes == cur_changes:
    print("You may wish to run again.")
else:
    print("Found", cur_changes, "total changes.")

if trivial_punctuation > 0:
    print(trivial_punctuation, "total trivial punctuation changes.")

file_name_bak = file_name + ".cpy"

f = open(file_name_bak, "w", newline="\n")
f.write(big_string)
f.close()

if launch_win_diff:
    if cur_changes == 0:
        print("Not launching diffs because there were no changes.")
    else:
        os.system("wm \"" + file_name_bak + "\" \"" + file_name + "\"")
        print("Running diffs.")

if copy_over:
    print("Copying file over.")
    copyfile(file_name_bak, file_name)

print(["Deleting", "Keeping"][save_copy], "backup file", file_name_bak)

if not save_copy:
    os.remove(file_name_bak)
