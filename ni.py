# ni.py
# python based replacement (of sorts) for batch files ni.bat and gh.bat
# they will be renamed niold.bat and ghold.bat
#
# check them for odd oneoffs to add to the flags before getting rid of the old file
#
# remember to check i7clash.py ni.py frequently as I add commands
#
# also, ni-remaining.bat will have a lot of stuff for special commands
# we want to go through them. This is intended to be a can-opener.
# special case: STS UNI universal (don't expand STS to stale-tales-slate? Or change the name? Or make i7.hdr(x) look for lower case as well or give it an option?)

import sys
import os
import re
from collections import defaultdict
from shutil import move, copy

import mytools as mt
import i7

ghsubdir = defaultdict(str)

to_project = i7.dir2proj()

potential_alternates = { 'ta': [ 'ra' ] }

materials_subdir = False
force_batch_move = False
source_opened = False
get_main_source = False
get_notes = False
get_fixes_file = False
goto_github = False
hfx_ary = []
user_project = ''
rbr_wild_card = ''
get_rbr = False
git_subdir = ''

temp_batch_file = "c:\\writing\\temp\\ni-temp.bat"
temp_batch_file_backup = "c:\\writing\\temp\\ni-temp-backup.bat"

ni_cfg = "c:/writing/scripts/ni.txt"

map_to = defaultdict(str) # this maps command line arguments to a specific file e.g. gglo (general global) = c:\Users\Andrew\Documents\github\gloco

def usage(header="Generic usage writeup"):
    mt.okay(header)
    mt.okay('=' * 50)
    print("This is a quasi-replacement for the batch file ni.bat.")
    print()
    mt.warn("Examples of usage:")
    print("ni t opens the source file in the current directory.")
    print("ni vf ta opens up VVFF's tables.")
    print("ni m opens up materials directory.")
    print()
    print("ni otf / dtf = opens / deletes temp file. Shorthand is o, while b opens the backup temp file from the previous run.")
    print("ni ?c / c? lists conflicts between ni.py-specific keywords (use s=) and general projects.")
    print()
    print("A backtick can be used to bypass command line flags. There is no harm in including it.")
    sys.exit()

def nometa(my_list):
    meta_commands = [ '?', '?c', 'c?', '`' ]
    lc = [x.lower() for x in my_list]
    if set([x.lower() for x in sys.argv]) & set(meta_commands):
        return False
    for x in lc:
        if x.startswith('s='):
            return False
    return True

def back_up_existing_temp(keep_original = False):
    if not os.path.exists(temp_batch_file):
        return
    if keep_original:
        copy(temp_batch_file, temp_batch_file_backup)
    else:
        move(temp_batch_file, temp_batch_file_backup)

def write_chdir_batch_file(my_chdir):
    f = open(temp_batch_file, "w")
    f.write("@echo off\n\n")
    f.write("cd {}\n".format(my_chdir))
    f.close()

def read_special_commands():
    with open(ni_cfg) as file:
        for (line_count, line) in enumerate (file, 1):
            l = line.lower().strip()
            if l.startswith("subdir"):
                l = re.sub("^.*?:", "", l)
                ary = l.split(',')
                print(ary)
                for a in ary:
                    a2 = a.split('=')
                    if a2[0] in ghsubdir:
                        mt.warn("Skipping redefinition of github subdir {} at line {}.".format(l[0], line_count))
                    else:
                        ghsubdir[a2[0]] = a2[1]
                continue
            if '=' not in l:
                if '~' in l:
                    mt.warn("Line {} should have = not ~. Replacing.")
                    l = l.replace('~', '-', 1)
                else:
                    continue
            a1 = l.split('=')
            if len(a1) > 2:
                mt.warn("WARNING line {} has >1 =.".format(len(a1)))
            a2 = a1[0].split(',')
            custom_file = a1[1]
            if custom_file.startswith('ch:'): # custom header
                custom_file = custom_file.replace('ch:', i7.extdir + '\\')
                if '.' not in custom_file:
                    custom_file = custom_file + '.i7x'
            if not os.path.exists(custom_file):
                mt.fail("NO SUCH FILE {} line {}".format(custom_file, line_count))
                continue
            for a in a2:
                if a in map_to:
                    mt.warn("Duplicate instance of {} in mapto file.".format(a))
                else:
                    map_to[a] = custom_file

cmd_count = 1

if len(sys.argv) == 1:
    mt.warn("No commands given to ni.py. Going to default directory. For usage, type ?")

read_special_commands()

if nometa(sys.argv[1:]):
    print("NOTE: if this didn't open the file or directory you want, use backtick ` or check for conflicts with ?c / c?.")

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if '-' in arg:
        if arg.count('-') > 1:
            mt.bailfail("Only one dash can be used after a project.")
        ary = arg.split('-')
        if ary[1] in ghsubdir:
            mt.okay("Going to subdir", ghsubdir[ary[1]])
            git_subdir = ghsubdir[ary[1]]
        else:
            mt.warn("Invalid ghsubdir value", ary[1])
        if not ary[0]:
            cmd_count += 1
            continue
        arg = ary[0]
    if arg == 'gh':
        goto_github = True
    elif arg == 't':
        get_main_source = True
    elif arg == 'rbr':
        get_rbr = True
    elif arg.startswith('rbr='):
        get_rbr = True
        rbr_wild_card = arg[4:]
    elif arg == '-':
        force_batch_move = True
    elif arg == 'm':
        materials_subdir = True
    elif arg == 'no':
        get_notes = True
    elif arg in ( 'fi', 'fix' ):
        get_fixes_file = True
    elif arg in ( 'd', 'dtf', 'dt', 'tfd', 'td' ):
        if os.path.exists(temp_batch_file):
            os.remove(temp_batch_file)
        else:
            mt.failbail("No {} to delete.".format(temp_batch_file))
        mt.bailokay("{} deleted.".format(temp_batch_file))
    elif arg in ( 'c', 'e' ):
        mt.npo(ni_cfg)
    elif arg in ( 'o', 'otf', 'ot', 'otf', 'tfo', 'to' ):
        if os.path.exists(temp_batch_file):
            mt.okay("Opening temp batch file {}.".format(temp_batch_file))
            mt.npo(temp_batch_file, print_cmd = False)
        else:
            mt.failbail("{} is not present.".format(temp_batch_file))
    elif arg in ( 'b', 'btf', 'bt', 'btf', 'tfb', 'tb' ):
        if os.path.exists(temp_batch_file_backup):
            mt.okay("Opening backup temp batch file {}.".format(temp_batch_file_backup))
            mt.npo(temp_batch_file_backup, print_cmd = False)
        else:
            mt.failbail("{} is not present.".format(temp_batch_file_backup))
    elif arg.startswith('s='):
        temp = arg[2:]
        if temp in map_to:
            mt.npo(map_to[temp])
        else:
            print(map_to)
            mt.bailfail("Bad value {} for s=.".format(temp))
    elif arg == '?':
        usage("USAGE")
    elif arg in ( '?c', 'c?' ):
        conflicts = [x for x in i7.i7x if x in map_to ]
        if len(conflicts):
            for c in conflicts:
                print("Conflict", c, map_to[c], i7.main_abb(c), i7.long_name(c))
        else:
            print("No conflicts.")
        sys.exit()
    elif arg in i7.i7hfx or arg in i7.i7hfxr:
        hfx_ary.append(arg)
    elif arg.replace('`', '') in i7.i7x:
        arg = arg.replace('`', '')
        if user_project:
            mt.bailfail("Defined 2 projects: {} and {}.".format(user_project, arg))
        user_project = arg
    elif arg in map_to:
        mt.warn(arg, "is in the map_to file, but it's safest to prefix it with s=.")
        m = map_to[arg]
        if os.path.isfile(m):
            mt.npo(map_to[arg])
        elif os.path.isdir(m):
            write_chdir_batch_file(m + '\\' + git_subdir if git_subdir else m)
            sys.exit()
        elif '{{}}' in m:
            sys.exit("Write formatting code later.")
        else:
            mt.fail(m, "is not a valid file or directory. You may need to fix the CFG file.")
            mt.npo(ni_cfg)
    elif os.path.exists('c:/games/inform/{}.inform'.format(arg.replace('`', ''))):
        arg = arg.replace('`', '')
        mt.warn("Using project unassigned in i7p.txt: {}.".format(arg))
        user_project = arg
    elif os.path.exists('c:/games/inform/{}'.format(arg.replace('`', ''))):
        arg = arg.replace('`', '')
        mt.warn("Using project flat directory in i7p.txt: {}.".format(arg))
        back_up_existing_temp()
        write_chdir_batch_file(os.path.join(i7.inform_root, arg.replace('`', '')))
        sys.exit()
    else:
        usage("Bad parameter {}. If you want to force a directory, you may want or need to use a backtick.".format(arg))
    cmd_count += 1

if 'glo' in hfx_ary:
    mt.warn("Just a general note that for the global general file, you use {}.".format(' or '.join([m for m in map_to if 'gloco' in map_to[m]])))

if user_project:
    to_project = user_project
elif not to_project:
    if i7.curdef:
        mt.warn("Going with default project from i7.txt, {}.".format(i7.curdef))
        to_project = i7.curdef
    else:
        back_up_existing_temp()
        mt.bailfail("Could not find project to act on.")

if get_main_source:
    main_source = i7.main_src(to_project)
    if not os.path.exists(main_source):
        mt.fail("Uh oh. This is bad. {} does not exist. Check for it in github, maybe?".format(main_source))
    print("Opening {} main source {}...".format(to_project, main_source))
    mt.npo(main_source, print_cmd = False, bail = False)
    source_opened = True

if get_fixes_file:
    fix_file = i7.fixes_file(to_project)
    if not os.path.exists(fix_file):
        mt.fail("Can't open fixes file", fix_file, "as it does not exist.")
    else:
        mt.npo(fix_file, print_cmd = False, bail = False)
        source_opened = True

if get_notes:
    notes_file = os.path.join(i7.proj2dir(to_project), "notes.txt")
    alt_notes_file = os.path.join(i7.ghbase, 'configs', 'notes', 'notes-{}.txt'.format(i7.main_abbr(to_project)))
    if not os.path.exists(notes_file):
        if os.path.exists(alt_notes_file):
            mt.warn(alt_notes_file, "exists but", notes_file, "does not, so going with config-repo file {}.".format(alt_notes_file))
            notes_file = alt_notes_file
        else:
            mt.bailfail("{} does not exist, and neither does its config-repo sibling {}. We may need to create it with noc or cno.".format(notes_file, alt_notes_file))
    print("Opening {} notes...".format(to_project))
    mt.npo(notes_file, print_cmd = False, bail = False)
    source_opened = True

if get_rbr:
    rbr_file = i7.rbr(to_project, file_type = rbr_wild_card)
    print("Opening rbr file", rbr_file)
    mt.npo(rbr_file, print_cmd = False, bail = False)

for h in hfx_ary:
    this_file = i7.hdr(to_project, h)
    if os.path.exists(this_file):
        mt.okay("Opening", this_file)
        mt.npo(this_file, bail=False, print_cmd = False)
        source_opened = True
    elif h == "glo":
        mt.warn("Since global headers were in the array, and {} has no global header, I'm opening the general GLOCO file.".format(to_project))
        mt.npo(i7.gloco)
    else:
        if to_project in i7.i7comr:
            umbrella_proj = i7.i7comr[to_project]
            umbrella_file = i7.hdr(umbrella_proj, h)
            if os.path.exists(umbrella_file):
                mt.warn(f"{to_project} had no {h} header, but the umbrella project {umbrella_proj} did. So I'm opening that.")
                mt.npo(umbrella_file)
        if h in potential_alternates:
            for p in potential_alternates[h]:
                this_alt_file = i7.hdr(to_project, p)
                print(this_alt_file)
                if os.path.exists(this_alt_file):
                    mt.warn("Opening alternate file", this_file)
                    mt.npo(this_alt_file, bail=False, print_cmd = False)
                    source_opened = True
        if not source_opened:
            mt.bailfail("Could not open {}.".format(this_file))

back_up_existing_temp()

if (not force_batch_move) and source_opened:
    sys.exit()

write_chdir_batch_file(i7.proj2dir(to_project, to_github = goto_github, materials = materials_subdir) + ('' if not git_subdir else '\\' + git_subdir))
