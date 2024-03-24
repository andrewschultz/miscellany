import os
import sys
import glob
import re
from pathlib import Path
from shutil import copy

from collections import defaultdict

#fixed
apple_base_folder = "c:\\emu\\appleold"

#options

cmd_count = 1
copy_string = ''
copy_last_back = False
copy_saved_back = False

diskmaps = defaultdict(list)
last_folder = ''

def read_dirs_files():
    global last_folder
    with open("c:/writing/scripts/nibcpy.txt") as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith('#'):
                continue
            if line.startswith(';'):
                break
            ary = line.lower().strip().split('=')
            diskmaps[ary[0]] = ary[1].split(',')

    # check to make sure we're somewhere valid
    current_dir = Path.cwd()
    last_folder = current_dir.name
    if last_folder not in diskmaps:
        sys.exit("Need to add last_folder {} to nibcpy.txt file".format(last_folder))
    else:
        print("In directory {}, {}".format(last_folder, diskmaps[last_folder]))

read_dirs_files()

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg == 'r':
        copy_saved_back = True
    elif arg == 'l':
        copy_last_back = True
        copy_saved_back = True
    else:
        if copy_string:
            sys.exit("You gave 2 potential copy over strings. I can only use one.")
        copy_string = arg
    cmd_count += 1

file_name_templates = diskmaps[last_folder]

if copy_last_back:
    if copy_string:
        sys.stderr.write("L option overrides copy_string. Use R to copy back a disk image other than the last.")
    first_prefix = diskmaps[last_folder][0]
    first_prefix = re.sub("%.*", "", first_prefix)
    print("First prefix", first_prefix)
    g = glob.glob(diskmaps[last_folder][0].replace('%', '*'))
    this_version = re.sub("\..*", "", g[-1])
    print("This version", this_version[len(first_prefix):])
    copy_string = this_version[len(first_prefix):]

change_file_array = [x.replace('%', copy_string) for x in diskmaps[last_folder]]

for f in file_name_templates:
    emu_file = os.path.join(apple_base_folder, f.replace('-%', ''))
    storage_file = f.replace('%', copy_string)
    if copy_saved_back:
        copy(storage_file, emu_file)
        os.system("attrib -r " + emu_file)
        print(storage_file, "copied successfully to", emu_file)
    else:
        copy(emu_file, storage_file)
        os.system("attrib +r " + storage_file)
        print(emu_file, "copied successfully to", storage_file)

sys.exit()
