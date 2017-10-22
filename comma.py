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
launch_win_diff = False

this_tabs = 0
last_tabs = 0

last_num = 0

max_changes = 25
cur_changes = 0

def leading_tabs(l):
    return len(l) - len(l.lstrip('\t'))

parser = argparse.ArgumentParser(description='semicolon to comma.', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-m', '--max_change', action='store', dest='max_changes', help='maximum changes', type=int)
parser.add_argument('-l', '--launchwindiff', action='store_true', dest='launch_win_diff', help='launch win diff')
parser.add_argument('-c', '--copyover', action='store_true', dest='copy_over', help='copy generated file back over')
parser.add_argument('-f', '--filename', action='store', dest='file_name', help='file name')
args = parser.parse_args()

if args.max_changes:
    max_changes = args.max_changes

if args.file_name:
    file_name = args.file_name

if args.launch_win_diff is True:
    launch_win_diff = True

if args.copy_over is True:
    copy_over = True

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
                print("WARNING line", count, "has extraneous else, tab compare this", cur_tabs, "that", this_tabs)
        else_next_bad = False
        if iffy:
            this_tabs = leading_tabs(line)
            if (re.search("\t(continue the action|the rule succeeds)", line) or re.search("\t.*instead;( \[.*\])?", line)) and not re.search("\tif ", line) and (this_tabs - last_tabs == 1):
                l2 = re.sub("^\t+", "", line).strip()
                last_line = re.sub(":+", ", " + l2, last_line)
                big_string = big_string + last_line
                cur_changes = cur_changes + 1
                else_next_bad = True
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
    copyfile(file_name_bak, file_name)
    print("Copied file over.")