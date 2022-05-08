# icl.py
#
# inform command line script in Python
#
# list all files and see if you can re-compile or need to. If something is there, and no files have been modified, that is a PASS.
# for x in (list of files): if date(link(x)) < date(compiled binary) then boom
# i7 needs a function that determines a compiled binary as well.
#   story.ni to auto.inf
# "c:/program files (x86)/Inform 7\Compilers\ni" -release -rules "c:/program files (x86)/Inform 7\Inform7\Extensions" -package "c:\games\inform\beta.inform" -extension="glulx"
#   compiling auto.inf
# "c:\Program Files (x86)\Inform 7\Compilers\inform-633" -kwSDG +include_path=..\Source,.\ auto.inf output.ulx
#   making binary into blorb
# "C:/Program Files (x86)/Inform 7/Compilers/cblorb" -windows Release.blurb Build/output.gblorb


from collections import defaultdict
import i7
import os
import time
import pendulum
import sys
import mytools as mt
import subprocess
import re
from shutil import copy

icl_cfg = "c:/writing/scripts/icl.txt"
default_proj_from_cfg = ''

my_build = i7.UNSPECIFIED
my_proj = ''
tried_one = False

what_to_build = [ False, False, False ]
build_projects = []

# variables from cmd line
file_change_threshold = 0
to_blorb = False
hide_stderr = False
hide_stdout = False
overwrite = True
compiler_version = '633'
launch_after = False
generic_blorb = False

build_states = defaultdict(list)
build_state_of_proj = defaultdict(str)

def usage(arg="USAGE FOR ICL.PY"):
    print(arg)
    print('=' * 50)
    print("b d r = beta debug release")
    print("bl = force to blorb")
    print("c# = use compiler version #")
    print("#(wdmhs) = threshold time to check for modification")
    print("-hs/he/eh/es = hide errors/std output for build")
    print("-no/on/ow/wo = (no) overwrite")
    print("l launches the newly built binary")
    print("use project name if necessary")
    exit()

def blorb_ext_of(bin_ext):
    if bin_ext == 'ulx':
        return 'gblorb'
    if bin_ext == 'z5' or bin_ext == 'z8':
        return 'zblorb'

def build_type(a):
    if a.startswith('b'): return i7.BETA
    if a.startswith('d'): return i7.DEBUG
    if a.startswith('r'): return i7.RELEASE
    sys.exit("Can't use build type with {}. B/D/R is required.".format(a))

def title_from_blurb(my_proj):
    blurb_file = "c:/games/inform/{}.inform/Release.blurb".format(i7.long_name(my_proj, use_given = True))
    with open(blurb_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if "[TITLE]" in line:
                (prefix, data) = mt.cfg_data_split(line)
                return data.replace('"', '')
    print("WARNING could not read blurb file", my_blurb)
    return ''

def read_icl_cfg():
    global compiler_version
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
            elif prefix == 'generic_blorb':
                global generic_blorb
                generic_blorb = mt.truth_state_of(data)
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
                    build_state_of_proj[i7.main_abb(x, use_given = True)] = my_varname
                continue
            if prefix == 'compver':
                compiler_version = data
                continue
            print("Unknown prefix", prefix, "line", line_count)

def derive_extension(this_project, this_build = i7.RELEASE, warn_default = True):
    this_project = i7.main_abb(this_project, use_given = True)
    if this_project in build_state_of_proj:
        return build_states[build_state_of_proj[this_project]][this_build]
    if warn_default:
        print("WARNING: defaulting to ulx extension because {} is not defined in {}.".format(this_project, icl_cfg))
        print("    This is okay for most large projects, but smaller projects may want a z8 definition.")
        print("    If the size seems bloated compared to building in the IDE, this might be why.")
    return 'ulx'

def last_proj_modified(this_proj, verbose=False):
    this_proj = i7.dictish(this_proj,i7.i7x)
    if this_proj in i7.i7f:
        my_files = i7.i7f[this_proj]
    else:
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
    return (time.time() - proj_tuple[0] < time_since, time.time() - proj_tuple[0])

def try_to_build(this_proj, this_build, this_blorb = False, overwrite = True, file_change_time = 0):
    if this_proj in i7.i7xr:
        this_proj = i7.i7xr[this_proj]
    output_ext = derive_extension(this_proj, this_build)

    if this_blorb and this_build != i7.RELEASE:
        print("WARNING: blorb should probably only be for release.")

    if this_build == i7.BETA:
        build_proj = 'beta'
        i7.create_beta_source(this_proj)
    else:
        build_proj = this_proj

    bin_out = i7.bin_file(this_proj, output_ext, this_build, this_blorb)

    bin_base = os.path.basename(bin_out)
    file_already_there = os.path.exists(bin_out)
    print("FINAL FILE {} {}.".format(bin_out, "already exists" if file_already_there else "not present"))
    (modified_recently_enough, modified_time_delta) = proj_modified_last_x_seconds(this_proj, file_change_time)
    if file_already_there:
        if not overwrite:
            sys.exit("You need to get rid of the no-overwrite flag, since the final file is there.")
        if not modified_recently_enough and file_change_time:
            print("Not building {}/{}/{} -- last files modified {} seconds ago, outside {} second boundary.".format(this_proj, this_build, bin_base, modified_time_delta, file_change_time))
            return
        print(bin_base, "already there.")
    print("Project {}modified last {} seconds.".format("" if modified_recently_enough else "not ", file_change_time))

    ext_flags = 'G' if output_ext == 'ulx' else output_ext.replace('z', 'v')
    build_flags = '-kw{}{}'.format('SD' if this_build == i7.DEBUG else '~S~D', ext_flags)
    # build flags need to be in RELEASE for Beta, since for Beta we just chop off a "not for release"

    i7.go_proj(build_proj)

    os.chdir("../Build")

    print("(ICL.PY) Creating auto.inf in {}".format(os.getcwd()))

    i7_to_i6 = [ "C:\\Program Files (x86)\\Inform 7\\Compilers\\ni",
      "-rules",
      "C:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions",
      "-package",
      i7.proj2root(build_proj), "-extension={}".format(output_ext)
      ]

    if this_build != i7.DEBUG:
        i7_to_i6.insert(1, "-release")

    mt.subproc_and_run( i7_to_i6, null_stdout = hide_stdout, null_stderr = hide_stderr )

    mt.print_status_of("auto.inf")

    print("(ICL.PY) Compiling auto.inf in {}".format(os.getcwd()))

    binary_out = "output.{}".format(output_ext)
    mt.subproc_and_run(
    [ 'C:\\Program Files (x86)\\Inform 7\\Compilers\\inform-{}'.format(compiler_version),
    build_flags,
    "+include_path=..\\Source,.\\",
    "auto.inf",
    binary_out
    ], null_stdout = hide_stdout, null_stderr = hide_stderr
    )

    to_run_after = os.path.abspath(binary_out)

    if this_build == i7.BETA:
        beta_out = "c:/games/inform/beta Materials/Release/beta-{}.{}".format(title_from_blurb('beta'), output_ext)
        print("Copying from", os.path.abspath(binary_out), "to", beta_out)
        copy(binary_out, beta_out)
        to_run_after = beta_out

    if not this_blorb:
        print("Not making blorb file. Toggle with bl.")

    else:

        if generic_blorb:
            blorb_file = 'Build/output.{}'.format(blorb_ext_of(output_ext))
        else:
            blorb_file = "{}/{}.{}".format(i7.proj2dir(this_proj, materials = True), title_from_blurb(this_proj), blorb_ext_of(output_ext))

        print("Creating blorb file", blorb_file)

        os.chdir("..")

        mt.subproc_and_run(
        [ 'C:\\Program Files (x86)\\Inform 7\\Compilers\\cblorb',
        '-windows',
        'Release.blurb',
        blorb_file
        ], null_stdout = hide_stdout, null_stderr = hide_stderr
        )

        mt.print_status_of(blorb_file)

    if launch_after:
        if not os.path.exists(to_run_after):
            print("Can't find", to_run_after, " so I won't launch it.")
            return
        if os.stat(to_run_after).st_size == 0:
            print(to_run_after, "is zero-byte, so I won't launch it.")
            return
        print("Launching", to_run_after)
        os.startfile(to_run_after)

read_icl_cfg()

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'debug':
        what_to_build[i7.DEBUG] = True
    elif arg == 'beta':
        what_to_build[i7.BETA] = True
    elif arg == 'release':
        what_to_build[i7.RELEASE] = True
    elif arg == 'l':
        launch_after = True
    elif arg[-1:] == 'w' and arg[:-1].isdigit():
        file_change_threshold = 604800 * int(arg[:-1])
    elif arg[-1:] == 'd' and arg[:-1].isdigit():
        file_change_threshold = 86400 * int(arg[:-1])
    elif arg[-1:] == 'h' and arg[:-1].isdigit():
        file_change_threshold = 3600 * int(arg[:-1])
    elif arg[-1:] == 'm' and arg[:-1].isdigit():
        file_change_threshold = 60 * int(arg[:-1])
    elif arg[-1:] == 's' and arg[:-1].isdigit():
        file_change_threshold = int(arg[:-1])
    elif mt.only_certain_letters("dbr", arg):
        what_to_build[i7.RELEASE] = 'r' in arg
        what_to_build[i7.DEBUG] = 'd' in arg
        what_to_build[i7.BETA] = 'b' in arg
    elif arg == 'bl' or arg == 'blorb':
        to_blorb = True
    elif arg in ( 'bg', 'gb' ):
        generic_blorb = True
    elif mt.alpha_match(arg, 'bgn'):
        generic_blorb = False
    elif arg == 'no' or arg == 'on':
        overwrite = False
    elif arg == 'wo' or arg == 'ow':
        overwrite = True
    elif arg == 'hs' or arg == 'sh':
        hide_stdout = True
    elif arg == 'eh' or arg == 'he':
        hide_stderr = True
    elif arg[0] == 'c' and arg[1].isdigit():
        compiler_version = arg[1:]
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
    elif arg == '?':
        usage()
    else:
        usage("Bad argument {}".format(arg))
    cmd_count += 1

if not my_proj:
    try_from_dir = i7.dir2proj(to_abbrev = True)
    if try_from_dir:
        print("You didn't specify a project, so I'm going with what your current directory suggests: {}.".format(try_from_dir))
        if default_proj_from_cfg:
            if try_from_dir == default_proj_from_cfg:
                print("It's the same as the default from the CFG.")
            else:
                print("To get the default from the CFG, {}, move to a different directory.".format(default_proj_from_cfg))
        my_proj = try_from_dir
    elif default_proj_from_cfg:
        print("You didn't specify a project, so I'm going with the default from the config, {}.".format(default_proj_from_cfg))
        my_proj = default_proj_from_cfg
    else:
        sys.exit("No project specified, none found in current directory or cfg file. Bailing.")

#sys.exit("Build: {} Projects: {}.".format(what_to_build, build_projects))

for x in range(0, 3): # DEBUG, RELEASE, BETA
    if what_to_build[x]:
        tried_one = True
        mod_blorb = True if x == i7.RELEASE else to_blorb
        try_to_build(my_proj, x, mod_blorb, overwrite, file_change_threshold)

for x in build_projects:
    tried_one = True
    try_to_build(x[0], x[1], to_blorb)

if not tried_one:
    sys.exit("You need to specify a build: b/eta, d/ebug or r/elease.")

