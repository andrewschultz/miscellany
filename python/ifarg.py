import os
import sys
import re
import mytools as mt
import glob
import pyperclip

ignores = []

temp_file = "c:\\writing\\temp\\ifarg-from-old.txt"

def try_line_open(my_file):
    any_bugs = False
    my_line = 0
    f2 = open(temp_file, "w")
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            new_line = line
            if re.search("if arg == .* or ", line):
                if not any_bugs:
                    print(my_file)
                    any_bugs = True
                    my_line = line_count
                x = re.findall("== ('.*?')", line)
                x_list = ', '.join(x)
                new_line = re.sub("if arg ==.*?:", "if arg in ( {} ):".format(x_list), line)
                print(line_count, line.rstrip())
                print(line_count, new_line.rstrip())
            f2.write(new_line)
    f2.close()
    if any_bugs:
        paste_string = "copy {} {}".format(temp_file, my_file)
        pyperclip.copy(paste_string)
        mt.wm(my_file, temp_file)
        sys.exit()

my_dir = "c:\\writing\\scripts"

g = glob.glob(my_dir + "\\*.py")

for f in g:
    if os.path.basename(f) in ignores:
        continue
    try_line_open(f)
