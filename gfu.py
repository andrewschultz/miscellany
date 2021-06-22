# gfu.py : git commit in the future (12:01 AM the next day or day specified)
#
# No, no, not gfY. gfu. Git future.
#
# sample usage: gfu.py FILESTUFF "COMMIT MESSAGE"
#

import pendulum
import i7
import os
import sys
import mytools as mt
import win32com.client

#schtasks /create /f /tn "Test" /tr "\"c:\program files\test.bat\" arg1 'arg 2 with spaces' arg3" /sc Daily /st 00:00

cmd_count = 1
my_files = ''
my_msg = ''
days_ahead = 1

trim_files = True

def git_wildcard(my_files):
    import subprocess
    x = subprocess.check_output(['git', 'ls-files', my_files]).decode()
    return x.strip().split("\n")

def delete_tasks_and_batches():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    folders = [scheduler.GetFolder('\\')]

    TASK_ENUM_HIDDEN = 1

    prefix = "future-gfu-"
    today_short = pendulum.now().add(days=1).format("MM/DD/YYYY").replace('/', '-')

    delete_and_before = prefix + today_short

    while folders:
        folder = folders.pop(0)
        folders += list(folder.GetFolders(0))
        tasks = list(folder.GetTasks(TASK_ENUM_HIDDEN))
        for task in tasks:
            tpl = task.Path.lower()
            if not 'future-gfu-' in tpl:
                continue
            if tpl > delete_and_before:
                continue
            del_sch = "schtasks /DELETE /F /TN {}".format(tpl)
            del_bat = "c:\\writing\\temp\\sched-{}.bat".format(today_short)
            print("Deleting", del_bat)
            os.remove(del_bat)
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

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    (arg_prefix, arg) = mt.prefix_div(arg, '=')
    if ' ' in arg or arg_prefix == 'm':
        if my_msg:
            sys.exit("Two messages.")
        my_msg = sys.argv[cmd_count]
    elif '.' in arg or '*' or arg_prefix == 'f':
        if my_files:
            sys.exit("Two file specs")
        my_files = sys.argv[cmd_count]
        if len(git_wildcard(my_files)) == 0:
            sys.exit("No wildcard found for file argument{}. Bailing.".format(my_files))
    elif arg == 'd':
        delete_tasks_and_batches()
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

if not my_files:
    sys.exit("No files defined.")
if not my_msg:
    sys.exit("No commit message.")

my_proj = i7.dir2proj(empty_if_unmatched = False)

if not my_proj:
	sys.exit("To run gfu, you need a valid project directory, preferably on github.")

tomorrow = pendulum.now()
tomorrow = tomorrow.add(days = days_ahead)
tomorrow_date = tomorrow.format("MM/DD/YYYY")

tomorrow_readable = tomorrow_date.replace("/", "-")
#future-add
task_name = "\"future-gfu-{}\"".format(tomorrow_readable)

batch_file = "c:\\writing\\temp\\sched-{}.bat".format(tomorrow_readable)

f = open(batch_file, "a")

f.write("\necho off\n\n")
f.write("cd {}\\{}\n\n".format(i7.gh_dir, my_proj))
f.write("git add {}\n\n".format(my_files))
f.write("git commit -m \"{}\"\n\n".format(my_msg))
f.write("echo GIT PUSH on your own time, especially if experimenting with this script and its products!\n\n")

f.close()

system_cmd = "schtasks /create /f /tn {} /tr \"{}\" /sc Once /sd {} /st 00:01".format(task_name, batch_file, tomorrow_date)

if trim_files:
    print("Trimming whitespace...")
    file_array = git_wildcard(my_files)
    for f in file_array:
        os.system("ttrim.py \"{}\"".format(os.path.realpath(f)))

print(system_cmd)
os.system(system_cmd)
print("To undo this, try:")
print("    schtasks /DELETE /F /TN {}".format(task_name))
print("    erase {}".format(batch_file))

