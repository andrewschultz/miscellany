from shutil import copyfile
import os
import re
import argparse

big_string = ""
iffy = False

went_over = False
else_next_bad = False

file_name = "story.ni"

copy_over = False
save_copy = False
launch_win_diff = False
unix_endings = True

this_tabs = 0
last_tabs = 0

last_num = 0

max_changes = 25
cur_changes = 0

max_collapse = 0
func_collapse = 0

def leading_tabs(l):
    return len(l) - len(l.lstrip('\t'))

parser = argparse.ArgumentParser(description='semicolon to comma.', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-m', '--max_change', action='store', dest='max_changes', help='maximum changes', type=int)
parser.add_argument('-mc', '--max_collapse', action='store', dest='max_collapse', help='maximum collapses', type=int)
parser.add_argument('-l', '--launchwindiff', action='store_true', dest='launch_win_diff', help='launch win diff')
parser.add_argument('-c', '--copyover', action='store_true', dest='copy_over', help='copy generated file back over')
parser.add_argument('-cs', '--copysave', action='store_true', dest='copy_save', help='copy generated file back over and save')
parser.add_argument('-s', '--save', action='store_true', dest='save_after', help='save generated file')
parser.add_argument('-f', '--filename', action='store', dest='file_name', help='file name')
parser.add_argument('-w', '--windows', action='store', dest='windows_endings', help='windows endings')
args = parser.parse_args()

if args.max_changes:
    max_changes = args.max_changes

if args.file_name:
    file_name = args.file_name

if args.launch_win_diff:
    launch_win_diff = True

if args.windows_endings:
    unix_endings = False

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

with open(file_name) as file:
    for line in file:
        count = count + 1
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
            if (re.search("\t(continue the action|the rule succeeds)", line) or re.search("\t.*instead;( \[.*\])?", line)) and not re.search("\t(if|unless) ", line) and (this_tabs - last_tabs == 1):
                l2 = re.sub("^\t+", "", line).strip()
                last_line = re.sub(":+", ", " + l2, last_line)
                big_string = big_string + last_line
                cur_changes = cur_changes + 1
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
        if re.search("\t+if ", line) and not re.search("instead;", line):
            if cur_changes < max_changes:
                iffy = True
                last_tabs = leading_tabs(line)
                continue
            elif cur_changes == max_changes:
                last_num = count
                went_over = True
        big_string = big_string + line

split_to_one_line = True

if split_to_one_line:
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
                        new_string = xxx[x+1] + re.sub("^\t", " ", xxx[x+2]) + comments
                        x = x + 3
                        xxx2.append(new_string)
                        func_collapse = func_collapse + 1
                        continue
        x = x + 1
        continue
    print(func_collapse, "collapsed functions.")
    big_string = '\n'.join(xxx2)

if cur_changes == 0 and func_collapse == 0:
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

file_name_bak = file_name + ".cpy"

f = open(file_name_bak, "w", newline="\n")
f.write(big_string)
f.close()

if launch_win_diff:
    os.system("wm \"" + file_name_bak + "\" \"" + file_name + "\"")
    print("Running diffs.")

if copy_over:
    print("Copying file over.")
    copyfile(file_name_bak, file_name)

print(["Deleting", "Keeping"][save_copy], "backup file", file_name_bak)

if not save_copy:
    os.remove(file_name_bak)
