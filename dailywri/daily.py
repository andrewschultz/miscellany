#
# daily.py
#
# common code for dsort.py and dgrab.py
#

from shutil import copy
import re
import os
import pendulum

today_file = pendulum.now().format("YYYYMMDD") + ".txt"

lower_bound = "20170101.txt"
upper_bound = today_file
days_back_start = days_back_end = total_files = 0

wri_temp = "c:/writing/temp"

def read_main_daily_config():
    global lower_bound
    global upper_bound
    global days_back_start
    global days_back_end
    global total_files
    with open("c:/writing/scripts/daily.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): continue
            if '=' not in line:
                print("CFG read warning: line {0} needs =".format(line_count))
                continue
            l = line.lower().strip().split("=")
            if l[0] == 'lower_bound': lower_bound = l[1]
            elif l[0] == 'upper_bound': upper_bound = l[1]
            elif l[0] == 'days_back_start': days_back_start = int(l[1])
            elif l[0] == 'days_back_end': days_back_end = int(l[1])
            elif l[0] == 'total_files': total_files = int(l[1])
            else: print("Uh oh unknown CFG value line {0} is {1}.".format(line_count, l[0]))
    if lower_bound > upper_bound:
        print("UH OH! Lower and upper bound are switched in the CFG. Flipping them.")
        (lower_bound, upper_bound) = (upper_bound, lower_bound)

def done_of(dir_path):
    return os.path.join(dir_path, "done")

def to_proc(dir_path):
    return os.path.join(dir_path, "to-proc")

toproc = proc = to_proc

def slashy_equals(dir_1, dir_list):
    for dir_2 in dir_list:
        d1 = dir_1.replace("\\", "/").lower()
        d2 = dir_2.replace("\\", "/").lower()
        if (d1 == d2): return dir_2
    return ""
    
def copy_to_done(file_name, dir_path):
    done_path = done_of(dir_path)
    done_from = os.path.join(dir_path, file_name)
    done_target = os.path.join(done_path, file_name)
    if not os.path.exists(done_target):
        print("Copying", done_from, "to", done_target)
        copy(done_from, done_target)

def valid_file(file_name, dir_name): # this should work for from_drive\drive_mod or 
    base_name = os.path.basename(file_name)
    if "daily" in dir_name or "from_drive" in dir_name: return re.search("^20[0-9]{6}\.txt$", base_name.lower())
    print("Bad dir name in", dir_name, "for", base_name)
    return False

