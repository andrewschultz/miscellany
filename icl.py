# icl.py
#
# inform command line script in Python
#
# list all files and see if you can re-compile or need to. If something is there, and no files have been modified, that is a PASS.
# for x in (list of files): if date(link(x)) < date(compiled binary) then boom
# i7 needs a function that determines a compiled binary as well.
# "c:/program files (x86)/Inform 7\Compilers\ni" -release -rules "c:/program files (x86)/Inform 7\Inform7\Extensions" -package "c:\games\inform\beta.inform" -extension="glulx"
#   C:\Program Files (x86)\Inform 7\Compilers\inform-633 -kwSDG +include_path=..\Source,.\ auto.inf output.ulx


from collections import defaultdict
import i7
import os
import time
import pendulum
import sys
import mytools as mt
import subprocess
import re

icl_cfg = "c:/writing/scripts/icl.txt"
default_proj_from_cfg = ''

my_build = i7.UNSPECIFIED
my_proj = ''
tried_one = False

cmd_count = 1
to_blorb = False

what_to_build = [ False, False, False ]
build_projects = []

build_states = defaultdict(list)
build_state_of_proj = defaultdict(str)

def usage(arg="USAGE FOR ICL.PY"):
    print(arg)
    print('=' * 50)
    print("b d r = beta debug release")
    print("bl = force to blorb")
    print("use project name if necessary")
    exit()

def build_type(a):
    if a.startswith('b'): return i7.BETA
    if a.startswith('d'): return i7.DEBUG
    if a.startswith('r'): return i7.RELEASE
    sys.exit("Can't use build type with {}. B/D/R is required.".format(a))

def read_icl_cfg():
    with open(icl_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#") or not line.strip(): continue
            if line.startswith(";"): break
            try:
                (prefix, data) = mt.cfg_data_split(line.strip().lower())
            except:
                print("Need a : or = to start line in the CFG:", line_count, line.strip())
                continue
            if prefix == "default":
                global default_proj_from_cfg
                if default_proj_from_cfg:
                    print("WARNING: redefining default project from CFG on line {}: {}")
                default_proj_from_cfg = data
                continue
            try:
                (my_varname, my_data) = mt.cfg_data_split(data)
            except:
                print("Need a : or = after the initial data marker", prefix, "at line", line_count)
                continue
            if prefix == 'ext':
                build_states[my_varname] = my_data.split(',')
                continue
            if prefix == 'type':
                for x in my_data.split(','):
                    build_state_of_proj[x] = my_varname
                continue
            print("Unknown prefix", prefix, "line", line_count)

def derive_extension(this_project, this_build = i7.RELEASE):
    if this_project not in build_state_of_proj:
        return 'ulx'
    return build_states[build_state_of_proj[this_project]][this_build]

def last_proj_modified(this_proj, verbose=False):
    my_files = i7.dictish(this_proj,i7.i7f)
    if not my_files:
        print("Could not find file list for {}--going with just story.ni.".format(this_proj))
        ms = i7.main_src(this_proj)
        if os.path.exists(ms):
            if verbose:
                print("Looking only at timestamp for the source.")
            my_files = [ms]
        else:
            sys.exit("No source for {}. Bailing.".format(this_proj))
    latest_time = 0
    latest_file = ""
    for x in my_files:
        this_time = os.stat(x).st_mtime
        ttt = pendulum.from_timestamp(this_time)
        # print(x, ttt, type(ttt), ttt.format("YYYY"))
        if this_time > latest_time:
            latest_time = this_time
            latest_file = x
    return(latest_time, latest_file)

def proj_modified_last_x_seconds(this_proj, time_since):
    proj_tuple = last_proj_modified(this_proj)
    return time.time() - proj_tuple[0] < time_since

def try_to_build(this_proj, this_build, this_blorb = False, overwrite = False, file_change_time = 86400):
    output_ext = derive_extension(this_proj, this_build)
    auto_file = i7.auto_file(this_proj)

    bin_out = i7.bin_file(this_proj, this_build)
    bin_base = os.path.basename(bin_out)
    file_already_there = os.path.exists(bin_out)
    print("{} {}.".format(bin_out, "already exists" if file_already_there else "not present"))
    modified_recently_enough = proj_modified_last_x_seconds(this_proj, file_change_time)
    if file_already_there:
        if not modified_recently_enough and not overwrite:
            print("Not building {}/{}/{} -- no files modified recently enough.".format(this_proj, this_build, bin_base))
            return
        print(bin_base, "already there.")
    print("Project {}modified last {} seconds.".format("" if modified_recently_enough else "not ", file_change_time))
    build_flags = '-kwSDG'
    if this_build == i7.RELEASE: build_flags = "-kw~S~DG"

    mt.subproc_and_run(
      [ "C:\\Program Files (x86)\\Inform 7\\Compilers\\ni",
      "-rules",
      "C:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions",
      "-package",
      "C:\\games\\inform\\{}.inform".format(i7.i7x[this_proj], "-extension={}'".output_ext)
      ]
      )

    print("Moved CWD to", os.getcwd())

    mt.subproc_and_run(
    [ 'C:\\Program Files (x86)\\Inform 7\\Compilers\\inform-632',
    build_flags,
    "+include_path=..\\Source,.\\",
    "auto.inf",
    "output.{}".format(output_ext)
    ]
    )

    i7.go_proj(my_proj)

read_icl_cfg()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'debug':
        what_to_build[i7.DEBUG] = True
    elif arg == 'beta':
        what_to_build[i7.RELEASE] = True
    elif arg == 'release':
        what_to_build[i7.BETA] = True
    elif mt.only_certain_letters("dbr", arg):
        what_to_build[i7.RELEASE] = 'r' in arg
        what_to_build[i7.DEBUG] = 'd' in arg
        what_to_build[i7.BETA] = 'b' in arg
    elif arg == 'bl' or arg == 'blorb':
        to_blorb = True
    elif arg == 'a' or arg == 'all':
        build_projects.extend([(my_proj, i7.DEBUG), (my_proj, i7.BETA), (my_proj, i7.RELEASE)])
    elif i7.main_abb(arg):
        my_proj = arg
    elif '/' in arg:
        y = arg.split("/")
        if len(y) != 2:
            sys.exit("Slashed argument needs exactly one slash.")
        if main_abb(y[1]):
            y.reverse()
        if y[1] == 'a':
            build_projects.extend([(my_proj, i7.DEBUG), (my_proj, i7.BETA), (my_proj, i7.RELEASE)])
        else:
            build_projects.append((y[0], build_type(y[1])))
    else:
        usage("Bad argument {}".format(arg))
    cmd_count += 1

#sys.exit("Build: {} Projects: {}.".format(what_to_build, build_projects))

for x in what_to_build:
    if x:
        tried_one = True
        try_to_build(my_proj, x)

for x in build_projects:
    tried_one = True
    try_to_build(x[0], x[1])

if not tried_one:
    sys.exit("You need to specify a build: b/eta, d/ebug or r/elease.")
    
