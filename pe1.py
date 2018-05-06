import sys
import os
import re
from shutil import copy

file_array = []

count = 1
copy_over = False

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c':
        copy_over = True
    else:
        temp_file_from_cmd = sys.argv[count]
        if not temp_file_from_cmd.lower().endswith('.py'):
            temp_file_from_cmd += '.py'
        file_array.append(temp_file_from_cmd)
    count += 1

if len(file_array) == 0:
    print("Going with default sc2.py")
    file_array = ['sc2.py']

def tidy_file(fn):
    if not os.path.exists(fn):
        sys.exit("No file {:s}".format(fn))
    print("Tidying", fn)
    got = 0
    temp_file = "tempscript.py"
    f = open(temp_file, "w")
    with open(fn) as file:
        for line in file:
            l2 = line
            if re.search(r'([\]\[a-z0-9_]+) = \1 \+ 1', line):
                l2 = re.sub(r'([\[\]a-z0-9_]+) = \1 \+ 1', r'\1 += 1', line)
                if l2 == line:
                    print("Oops tagged but not changed line", line.strip())
                else:
                    got += 1
            elif '+ 1' in line:
                print(line.strip())
            f.write(l2)
    f.close()
    if got:
        if copy_over:
            copy(temp_file, fn)
            print(fn, "had", got, "lines changed.")
        else:
            os.system("wm {:s} {:s}".format(fn, temp_file))
    else:
        print("No changes for", fn)
    os.remove(temp_file)

for x in file_array:
    tidy_file(x)

exit()
