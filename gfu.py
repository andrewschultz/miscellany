# gfu.py : git commit in the future (12:01 AM the next day or day specified)
#
# No, no, not gfY. gfu. Git future.
#
# sample usage: gfu.py FILESTUFF "COMMIT MESSAGE"
#
# todo:
#   detect if batch file to be deleted is present
#   detect if task to be deleted is present
#

import pendulum
import i7
import os
import sys
import mytools as mt
import win32com.client
import subprocess
import ctypes
import re
import glob

#schtasks /create /f /tn "Test" /tr "\"c:\program files\test.bat\" arg1 'arg 2 with spaces' arg3" /sc Daily /st 00:00

cmd_count = 1
my_files = ''
my_msg = ''
days_ahead = 1
zappable = ''

look_for_files = False
trim_files = True

prefix = "future-gfu-"
gfu_temp = "c:/writing/temp/gfu-temp.txt"

def git_wildcard(my_files):
    x = subprocess.check_output(['git', 'ls-files', my_files]).decode()
    return [y.strip() for y in x.split("\n") if y.strip()]
    return x.strip().split("\n")

def git_staged():
    x = subprocess.check_output(['git', 'diff', '--name-only', '--cached']).decode()
    return [y.strip() for y in x.split("\n") if y.strip()]

def get_future_tasks(prefix):
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    folders = [scheduler.GetFolder('\\')]

    TASK_ENUM_HIDDEN = 1

    my_array = ''

    while folders:
        folder = folders.pop(0)
        folders += list(folder.GetFolders(0))
        tasks = list(folder.GetTasks(TASK_ENUM_HIDDEN))
        for task in tasks:
            tpl = task.Path.lower()
            if not tpl.startswith(prefix):
                continue
            my_array.append(task)

    return my_array

def delete_tasks_and_batches():
    today_short = pendulum.now().add(days=1).format("MM/DD/YYYY").replace('/', '-')
    delete_and_before = prefix + today_short
    for x in my_future_tasks:
        if x > delete_and_before:
            continue
        del_sch = "schtasks /DELETE /F /TN {}".format(tpl)
        del_bat = "c:\\writing\\temp\\sched-{}.bat".format(today_short)
        if os.path.exists(del_bat):
            print("Deleting", del_bat)
            os.remove(del_bat)
        else:
            print("No batch file corresponding to", today_short)
        print("Task remove command", del_sch)
        os.system(del_sch)

    sys.exit()

def next_from_batches():
    currently_ahead = 1
    while 1:
        base = pendulum.now().add(days = currently_ahead)
        base_date = base.format("MM-DD-YYYY")
        base_file = "c:\\writing\\temp\\sched-{}.bat".format(base_date)
        if not os.path.exists(base_file):
            return currently_ahead
        currently_ahead += 1

def print_tasks_and_batches():
    g1 = sorted(glob.glob("c:/writing/temp/sched-*.bat"))
    if not len(g1):
        print("No batch files.")
    else:
        print("Batch files")
        for g in g1:
            print("    --->", g)
    if not len(my_future_tasks):
        print("No scheduled tasks.")
    else:
        print("Scheduled tasks")
        for g in my_future_tasks:
            print("    --->", g)

def usage(my_msg = "Usage for gfu.py"):
    print("================", my_msg)
    print("d to delete stuff. Otherwise, you need entries for commit message and file selection.")
    print("nt/t toggles file trimming.")
    print("# number adds to a file (#) days ahead, n adds to next open day.")
    print("The program scans for spaces in arguments, so use quotes. You can also use f=files, m=messages, d=dates.")
    print()
    print("The path argument must have . or * in it. The commit must have a space.")
    print()
    print("EXAMPLE: gfu.py FILESTUFF \"COMMIT MESSAGE\" n <---commits 12:01 AM next available day.")
    sys.exit()

my_future_tasks = get_future_tasks('future-gfu')

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    (arg_prefix, arg) = mt.prefix_div(arg, '=')
    if arg_prefix == 'l' and arg:
        look_for_files = True
        files_to_check = git_wildcard(sys.argv[cmd_count][2:])
    elif ' ' in arg or arg_prefix == 'm':
        if my_msg:
            sys.exit("Two messages.")
        my_msg = sys.argv[cmd_count]
    elif arg_prefix == 'z':
        print("Got zappable")
        zappable = arg
        if not re.search("^[0-9]{2}-[0-9]{2}-[0-9]{4}$", zappable):
            print("Zappable file/task must be of the form ##-##-####.")
            sys.exit()
    elif '.' in arg or '*' in arg or arg_prefix == 'f': # place arg prefixes above this
        if my_files:
            sys.exit("Two file specs")
        my_files = sys.argv[cmd_count]
        if arg_prefix:
            my_files = my_files[2:]
        if len(git_wildcard(my_files)) == 0:
            sys.exit("No wildcard found for file argument {}. Bailing.".format(my_files))
    elif arg == 'd':
        delete_tasks_and_batches()
    elif arg in ('l', 'lo'):
        if arg == 'lo':
            sys.stdout = open(gfu_temp, "w")
        print_tasks_and_batches()
        sys.stdout = sys.__stdout__
        if arg == 'lo':
            mt.npo(gfu_temp)
        sys.exit()
    elif arg == 't':
        trim_files = True
    elif arg in ( 'nt', 'tn' ):
        trim_files = False
    elif arg.isdigit():
        sys.exit("d/days= needs an integer after.")
    elif arg == 'n':
        days_ahead = next_from_batches()
        print("First open day is", days_ahead, "day{} ahead".format(mt.plur(days_ahead)))
    elif arg == '?':
        if arg_prefix:
            print("WARNING unrecognized prefix", arg_prefix)
        usage()
    else:
        usage("Bad argument {}".format(sys.argv[cmd_count]))
    cmd_count += 1

if look_for_files:
    staged_array = git_staged()
    popup_string = ""
    for x in files_to_check:
        if x in staged_array:
            popup_string += "{}\n".format(os.path.abspath(x))
    if popup_string:
        popup_string = pendulum.now().format("MM/DD/YYYY HH:mm:ss") + "\n\n" + popup_string
        messageBox = ctypes.windll.user32.MessageBoxW
        messageBox(None, popup_string, "Still staged after git commit {}".format(sys.argv[cmd_count][2:]), 0x0)
    else:
        print("Everything that should be committed, is.")

if zappable:
    sched_bat = "c:\\writing\\temp\\sched-{}.bat".format(zappable)
    print("Zapping {}".format(sched_bat))
    os.system("erase {}".format(sched_bat))
    sched_del = "schtasks /DELETE /F /TN {}".format(zappable)
    print("Zapping task with {}".format(sched_del))
    os.system(sched_del)
    sys.exit()

if look_for_files:
    sys.exit()

if not my_files:
    sys.exit("No files defined.")
if not my_msg:
    sys.exit("No commit message.")

my_proj = i7.dir2proj(empty_if_unmatched = False)

if not my_proj:
	sys.exit("To run gfu, you need a valid project directory, preferably on github.")

future_date = pendulum.now()
future_date = future_date.add(days = days_ahead)
future_date_date = future_date.format("MM/DD/YYYY")

future_date_readable = future_date_date.replace("/", "-")
#future-add
task_name = "\"{}-{}\"".format(prefix,future_date_readable)

batch_file = "c:\\writing\\temp\\sched-{}.bat".format(future_date_readable)

file_array = git_wildcard(my_files)

full_file_array = [os.path.realpath(x) for x in file_array]

zap_cmd = "gfu.py \"l={}\" \"z={}\"".format(my_files, future_date_date)

if trim_files:
    print("Trimming whitespace...")
    for f in file_array:
        os.system("ttrim.py \"{}\"".format(os.path.realpath(f)))

for f in full_file_array:
    os.system("attrib +r \"{}\"".format(f))

fout = open(batch_file, "a")

fout.write("\necho off\n\n")
fout.write("cd {}\\{}\n\n".format(i7.gh_dir, my_proj))
fout.write("git add {}\n\n".format(my_files))
fout.write("git commit -m \"{}\"\n\n".format(my_msg))

fout.write("{}\n\n".format(zap_cmd))
fout.write("echo GIT PUSH on your own time, especially if experimenting with this script and its products!\n\n")

for f in full_file_array:
    fout.write("attrib -r \"{}\"\n\n".format(f))

fout.close()

mt.npo(batch_file)

sys.exit()

system_cmd = "schtasks /create /f /tn {} /tr \"{}\" /sc Once /sd {} /st 00:01".format(task_name, batch_file, future_date_date)

print(system_cmd)
os.system(system_cmd)
print("To undo this, try:")
print("    schtasks /DELETE /F /TN {}".format(task_name))
print("    erase {}".format(batch_file))
print(" or {}".format(zap_cmd))
