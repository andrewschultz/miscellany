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
look_for_cmd_force = False
run_cmd = True

projects = defaultdict(list)
final_count = defaultdict(lambda: defaultdict(list))

ghd_info = "c:/writing/scripts/ghd.txt"
ghd_cmd = "c:/writing/scripts/ghd-cmd.txt"
ghd_results = "c:/writing/temp/ghd-results.txt"

base_dir = mt.gitbase

def usage(my_param = ""):
    if (my_param):
        print("=================bad argument", my_param)
    else:
        print("=================Usage for ghd.py")
    print("p  = windows popup box")
    print("d# = days back")
    print("l = look for command, lf = force command, nr = don't run command")
    print("cv = checks commit validity")
    print("e/es/se edits main, ei/ie edits config, ec/ce edits command file, er/re edits results file")
    print("NOTE: to add to {}, run gfu.py instead.".format(os.path.basename(ghd_cmd)))
    sys.exit()

def last_commit_data():
    temp = subprocess.check_output([ 'git', 'log' ]).decode()
    return temp # we can do better than this, because we just want the exact log message, but right now, this is good enough.

def check_commit_validity():
    with open(ghd_cmd) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#") or not line.strip():
                continue
            (proj, data) = mt.cfg_data_split(line)
            my_dir = i7.proj_exp(proj, return_nonblank = (proj in ignorables), to_github = True)
            if not my_dir:
                mt.win_or_print("OH NO! BAD COMMAND", "Check {} for commands.", windows_popup_box, bail = False)
                continue
            os.chdir(os.path.join(i7.gh_dir, my_dir))
            dary = data.split(";")
            gh_files_wild = dary[0].split(",")
            gh_files = []
            for g in gh_files_wild:
                result = subprocess.run( [ 'git', 'diff', '--cached', '--name-only', g ], stdout=subprocess.PIPE ).stdout.decode().split("\n")
                gh_files.extend(result)
                result = subprocess.run( [ 'git', 'diff', '--name-only', g ], stdout=subprocess.PIPE ).stdout.decode().split("\n")
                gh_files.extend(result)
            gh_files = sorted(list(set([x for x in gh_files if x])))
            if len(gh_files) == 0:
                print("WARNING no-longer-valid line {}: {}".format(line_count, line.strip()))
            else:
                print("Okay line {}: {}".format(line_count, line.strip()))
    sys.exit()

def check_prestored_command(run_cmd = True): # sample line misc:i7/pl/i7.pl;
    look_for_cmd = True
    new_file_string = ""
    return_val = ''
    commits_left = 0
    stored_commit_message = "<NO COMMIT MESSAGE>"
    got_any = False
    with open(ghd_cmd) as file:
        for (line_count, line) in enumerate (file, 1):
            if got_any or line.startswith("#") or not line.strip():
                new_file_string += line
                if not line.startswith("#"):
                    commits_left += 1
                continue
            (proj, data) = mt.cfg_data_split(line)
            my_dir = i7.proj_exp(proj, return_nonblank = (proj in ignorables), to_github = True)
            if not my_dir:
                mt.win_or_print("OH NO! BAD COMMAND", "Check {} for commands.", windows_popup_box, bail = False)
            else:
                os.chdir(os.path.join(i7.gh_dir, my_dir))
                dary = data.split(";")
                gh_files_wild = dary[0].split(",")
                gh_files = []
                for g in gh_files_wild:
                    result = subprocess.run( [ 'git', 'ls-files', g ], stdout=subprocess.PIPE ).stdout.decode().split("\n")
                    gh_files.extend(result)
                gh_files = sorted(list(set([x for x in gh_files if x])))
                for gh_file in gh_files:
                    print("Trimming", gh_file)
                    os.system("ttrim.py -c {}".format(gh_file))
                gitadd_cmd = "git add {}".format(' '.join(dary[0].split(",")))
                gitcommit_cmd = "git commit -m \"{}\"".format(dary[1])
                stored_commit_message = dary[1]
                check_log_prev = last_commit_data()
                if dary[1] in check_log_prev:
                    print("It looks like your commit message is already in the previous commit. So you are likely duplicating your efforts.")
                    return ''
                if run_cmd:
                    os.system(gitadd_cmd)
                    os.system(gitcommit_cmd)
                else:
                    print("Would've run:")
                    print("    ", gitadd_cmd)
                    print("    ", gitcommit_cmd)
                check_log = last_commit_data()
                if run_cmd and check_log == check_log_prev:
                    print("Oops! The commit from line {} failed: {}".format(line_count, dary[1]))
                    return_val = ''
                    new_file_string += line
                else:
                    print("Everything worked on line {}: {}".format(line_count, dary[1]))
                    f = open(ghd_results, "w")
                    f.write("NOTE: successfully created commit automatically with ghd.py\n\n")
                    if run_cmd:
                        f.write("NOTE 2: this is actually a test run. Here's what would've been printed:\n\n")
                    f.write("It went to the {} repository.\n\n".format(my_dir))
                    f.write("The {} {}.\n\n".format('file committed was' if len(gh_files) == 1 else 'files committed were', ', '.join(gh_files)))
                    f.write("The commit message was >>{}<<\n\n".format(dary[1]))
                    f.write("The time of day was >>{}<<\n\n".format(pendulum.now().format("YYYY MM DD HH:mm:ss")))
                    f.close()
                    mt.file_in_browser(ghd_results)
                    return_val = my_dir
                    got_any = True
    if run_cmd:
        f = open(ghd_cmd, "w")
        f.write(new_file_string)
        f.close()
    else:
        print("Not rewriting", ghd_cmd, "since this is a test run.")
    if got_any:
        mt.win_or_print("Created a commit in the {} repository.\n\Commit text={}.\n\nFiles={}.\n\n{} commit{} left.\n\nReset with:\n\ngit reset HEAD~1".format(
            my_dir, stored_commit_message, '!', commits_left, mt.plur(commits_left)), "Pushed a late-night commit", True, bail = True)
    elif not len(final_count):
        mt.win_or_print("NO CHANGES TODAY (yet)", this_header, windows_popup_box, bail = True)
    sys.exit()

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
    global look_for_cmd
    global look_for_cmd_force
    global run_cmd
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
        elif arg == 'lf':
            look_for_cmd_force = True
        elif arg in ( 'e', 'es', 'se'):
            mt.npo(__file__)
        elif arg in ( 'ei', 'ie' ):
            mt.npo(ghd_info)
        elif arg in ( 'ec', 'ce' ):
            mt.npo(ghd_cmd)
        elif arg in ( 'er', 're' ):
            mt.npo(ghd_results)
        elif arg == 'cv':
            check_commit_validity()
        elif arg == 'nr':
            run_cmd = False
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

if look_for_cmd_force or (look_for_cmd and not len(final_count)): # usage here is misc:x.pl,y.pl;COMMIT MESSAGE
    check_prestored_command(run_cmd)

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
