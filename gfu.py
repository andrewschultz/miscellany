# gfu.py : git commit in the future (12:01 AM the next day)

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

def usage():
    print("d to delete stuff. Otherwise, you need entries for commit message and file selection.")
    sys.exit()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if ' ' in arg:
        if my_msg:
            sys.exit("Two messages.")
        my_msg = sys.argv[cmd_count]
    elif '.' in arg or '*' in arg:
        if my_files:
            sys.exit("Two file specs")
        my_files = sys.argv[cmd_count]
    elif arg == 'd':
        delete_tasks_and_batches()
    elif arg.isdigit():
        days_ahead = int(arg)
    else:
        usage()
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

print(system_cmd)
os.system(system_cmd)

