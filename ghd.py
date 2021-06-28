#
# ghd.py
# perl github daily checker
#
# todo: put ignorables to CFG file
#

import sys
import os
import i7
import mytools as mt
from collections import defaultdict
import subprocess
import pendulum

ignorables = [ 'misc', 'writing', 'configs' ]

days_back = 0

this_header = "Daily Github commits "
total_count = 0

windows_popup_box = False
look_for_cmd = False

projects = defaultdict(list)
final_count = defaultdict(lambda: defaultdict(list))

ghd_info = "c:/writing/scripts/ghd.txt"
ghd_cmd = "c:/writing/scripts/ghd-cmd.txt"
base_dir = mt.gitbase

def usage(my_param):
    if (my_param):
        print("=================bad argument", my_param)
    else:
        print("USage for ghd.py")
    print("p  = windows popup box")
    print("d# = days back")
    print("l = look for command")
    print("e/es/se edits main, ec/ce edits config")
    sys.exit()

def check_prestored_command():
    look_for_cmd = True
    new_file_string = ""
    if look_for_cmd:
        got_any = False
        with open(ghd_cmd) as file:
            for (line_count, line) in enumerate (file, 1):
                if got_any or line.startswith("#"):
                    new_file_string += line
                    continue
                got_any = True
                (proj, data) = mt.cfg_data_split(line)
                my_dir = i7.proj_exp(proj, return_nonblank = (proj in ignorables), to_github = True)
                if not my_dir:
                    mt.win_or_print("OH NO! BAD COMMAND", "Check {} for commands.", windows_popup_box, bail = False)
                else:
                    os.chdir(os.path.join(i7.gh_dir, my_dir))
                    dary = data.split(";")
                    gh_files = dary[0].split(",")
                    for gh_file in gh_files:
                        os.system("ttrim.py -c {}".format(gh_file))
                    gitadd_cmd = "git add {}".format(' '.join(dary[0].split(",")))
                    os.system(gitadd_cmd)
                    gitcommit_cmd = "git commit -m \"{}\"".format(dary[1])
                    os.system(gitcommit_cmd)
                    check_log = subprocess.check_output([ 'git', 'log', '-1' ]).decode()
                    if dary[1] in check_log:
                        print("Everything worked!")
                    else:
                        print("Oops! Something failed.")
        f = open(ghd_cmd, "w")
        f.write(new_file_string)
        f.close()
    mt.win_or_print("NO CHANGES TODAY (yet)", this_header, windows_popup_box, bail = True)

def read_cfg_file():
    with open(ghd_info) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            (prefix, data) = mt.cfg_data_split(line)
            if prefix == 'base':
                global base_dir
                base_dir = data
                continue
            projects[prefix] = data.split(",")

def read_cmd_line():
    cmd_count = 1
    global windows_popup_box
    global days_back
    while cmd_count < len(sys.argv):
        arg = mt.nohy(sys.argv[cmd_count])
        if arg =='p':
            windows_popup_box = True
        elif arg == 'pn' or arg == 'np':
            windows_popup_box = False
        elif arg[0] == 'd' and arg[1:].isdigit():
            days_back = int(arg[1:])
        elif arg.isdigit():
            days_back = int(arg)
        elif arg == 'l':
            look_for_cmd = True
        elif arg == 'e' or arg == 'es' or arg == 'se':
            mt.npo(__main__)
        elif arg == 'ec' or arg == 'ce':
            mt.npo(ghd_info)
        elif arg == '?':
            usage()
        else:
            usage(arg)
        cmd_count += 1

def process_result(output_text):
    lines = output_text.splitlines()
    output_array = []
    read_next_line = False
    for x in lines:
        if x.startswith("Date"):
            read_next_line = True
            continue
        if read_next_line and x.strip():
            read_next_line = False
            output_array.append(x.strip())
    return output_array

#################################################

os.chdir(base_dir)

read_cfg_file()
read_cmd_line()

this_header += pendulum.today().subtract(days=days_back).format("YYYY-MM-DD")

for x in projects:
    for y in projects[x]:
        try:
            os.chdir(os.path.join(mt.gitbase, y))
        except:
            print("Bad github subdir", y, "in", x)
            continue
        proc_array = [ 'git', 'log' ]
        if days_back == 0:
            proc_array.append('--since="00:00:00"')
        else:
            proc_array.append('--since="{} days ago 00:00" --until="{} days ago 00:00"'.format(days_back, days_back - 1))
        result = subprocess.check_output(proc_array)
        if not result:
            continue
        output_array = process_result(result.decode())
        if output_array:
            final_count[x][y] = output_array

if 1 or not len(final_count): # usage here is misc:x.pl,y.pl;COMMIT MESSAGE
    check_prestored_command()

out_string = ""

for f in sorted(final_count):
    proj_ary = []
    local_count = 0
    for g in sorted(final_count[f]):
        my_len = len(final_count[f][g])
        proj_ary.append("{} ~ {}".format(g, my_len))
        total_count += my_len
        local_count += my_len
    out_string += "{}{}: {}\n".format(f.upper(), ' ({})'.format(local_count) if len(final_count) > 1 and len(final_count[f]) > 1 else '', ', '.join(proj_ary))

out_string = "TOTALS: {}\n".format(total_count) + out_string
out_string = out_string.rstrip()
mt.win_or_print(out_string, this_header, windows_popup_box, bail = True)
