# gq.py
#
# replaces gq.pl
#
# usage gq.py as match_string_array (for alex smart)
#       gq.py `as to search for the word AS, '/' = a bunch of non alpha words, '!' does negative lookbehind
# can use any number of words. mn# specifices minimum matches needed, with some error checking
# todo: plurals option (only when I can't think of anything else to do)
#       speedup for allowed_misses
#
# to enable colors by default: REG ADD HKCU\CONSOLE /f /v VirtualTerminalLevel /t REG_DWORD /d 1
# I'd assume deleting this or changing it to zero would disable colors
#
# todo: revamp fast_match option as it is broken now that strings can look for multiple matches
#

from collections import defaultdict
import mytools as mt
import re
import i7
import sys
import os
import colorama

# variables potentially in CFG file

max_overall = 100
max_in_file = 25
history_max = 100
colors = True
fast_match = True
verbose = False
all_similar_projects = True
my_proj = ""

# constants

hdr_equals = '=' * 25

my_cfg = "c:/writing/scripts/gqcfg.txt"

# coloring stuff
colorama.init()
color_ary = [ colorama.Fore.GREEN, colorama.Fore.BLUE, colorama.Fore.YELLOW, colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Fore.RED ]
header_color = -1

# options only on cmd line

user_input = False
view_history = False
post_open_matches = False

include_notes = True

modify_line = True

ALL=0
INSIDE=1
OUTSIDE=2

quote_status = ALL

user_specified_matches_needed = 0

# Keep this false or you may overwrite something
create_new_history = False

# variables not in CFG file/cmd line

first_loop = True
found_overall = 0

frequencies = defaultdict(int)

match_string_array = []
default_from_cwd = i7.dir2proj()
default_from_cfg =  ""

TAGS = 0
PARENTHESES = 1
BRACKETS = 2
CURLY_BRACKETS = 3
highlight_repeat = 4
highlight_types = {
  TAGS: "<>",
  PARENTHESES: "()",
  BRACKETS: "[]",
  CURLY_BRACKETS: "{}"
}
my_highlight = TAGS

def usage():
    print("You can type in 1-2 words to match. ` means to take a word literally: `as is needed for as. ! means negative lookbehind, ~ means negative lookahead, / means only nonalpha characters between matching words")
    print("    !~ can also use \b if you want to demarcate word boundaries. More than one word = ! ORs all but last, ~ ORs all but first. pon=y=ies searches for pony or ponies.")
    print()
    print("You may also specify a project or combinations e.g. sts and roi do the same thing by default. r is a shortcut for roi")
    print("o = only this project, a = all similar projects")
    print()
    print("vh = view history file of a project, what you have searched")
    print("mf/mo=# sets maximum file/overall matches")
    print("po postopens matches, npo/opn kills it")
    print("v/q = verbose/quiet")
    print("nn/yn/ny = toggle searching notes file")
    print()
    print("fm = fast match (on by default, no accuracy loss)")
    print("e/ec/ce = edit config file")
    print("qi/qo/qa = quotes inside/outside/all")
    print("con/coff = colors on/off")
    print("ml/nml/mln = whether or not to modify line where search results are found")
    exit()

def left_highlight(color_idx):
    return f'{color_ary[color_idx % len(color_ary)]}{highlight_types[my_highlight][0] * highlight_repeat}'

def right_highlight():
    return f'{highlight_types[my_highlight][1] * highlight_repeat}{colorama.Style.RESET_ALL}'

def hist_file_of(my_proj):
    return os.path.normpath(os.path.join("c:/writing/scripts/gqfiles", "gq-{}.txt".format(i7.combo_of(my_proj))))

def write_history(my_file, my_query, create_new_history = False):
    if create_new_history:
        if os.path.exists(my_file):
            print(my_file, "exists. If you can't write to it, check it manually.")
            sys.exit()
        f = open(my_file, "w")
        f.close()
    try:
        f = open(my_file, "r")
    except:
        print("File open failed for", my_file, "so I'll make you create it with -newhist.")
        sys.exit()
    ary = [x.strip() for x in f.readlines()]
    f.close()
    if my_query == ary[0]:
        print("Not rewriting since {} is already the first element.".format(my_query))
        return
    if my_query in ary:
        print(my_query, "already in history.")
        ary.remove(my_query)
    ary.insert(0, my_query)
    if len(ary) > history_max:
        print("Removing excess history",', '.join(ary[history_max:]))
        ary = ary[:history_max]
    f = open(my_file, "w")
    f.write("\n".join(ary))
    f.close()

def read_cfg():
    if not os.path.exists(my_cfg):
        print("Could not find CFG file", my_cfg)
        print("This is not a fatal error, since variables are defined in the script itself. But you can adjust variables there.")
        return
    with open(my_cfg) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if '=' in line:
                (prefix, data) = mt.cfg_data_split(line)
                if prefix == "all_similar_projects":
                    global all_similar_projects
                    all_similar_projects = mt.truth_state_of(data)
                elif prefix == "colors":
                    global colors
                    colors = mt.truth_state_of(data)
                elif prefix == "default_from_cfg":
                    global default_from_cfg
                    default_from_cfg = data
                elif prefix == "fast_match":
                    global fast_match
                    fast_match = mt.truth_state_of(data)
                elif prefix == "max_overall":
                    global max_overall
                    max_overall = int(data)
                elif prefix == "min_overall":
                    global min_overall
                    min_overall = int(data)
                elif prefix == "verbose":
                    global verbose
                    verbose = mt.truth_state_of(data)
                else:
                    print("Unknown = reading CFG, line", line_count, line.strip())

def find_text_in_file(match_string_array, projfile):
    global found_overall
    bf = i7.inform_short_name(projfile)
    if found_overall == max_overall:
        return -1
    found_so_far = 0
    current_table = ""
    current_table_line = 0
    with open(projfile) as file:
        for (line_count, line) in enumerate (file, 1):
            if current_table:
                current_table_line += 1
                if not line.strip():
                    current_table = ""
            if line.startswith("table of") and not current_table:
                current_table = re.sub(" *\[.*", "", line.strip().lower())
                current_table_line = -1
            if quote_status == OUTSIDE:
                ary = line.split('"')
                line = ' '.join(ary[::2])
            elif quote_status == INSIDE:
                ary = line.split('"')
                line = ' '.join(ary[1::2])
            line_out = line.strip()
            found_this_line = 0
            for match_idx in range(0, len(match_string_array)):
                if re.search(match_string_array[match_idx], line, flags=re.IGNORECASE):
                    found_this_line += 1
                    if modify_line:
                        line_out = re.sub(match_string_array[match_idx], lambda x: "{}{}{}".format(left_highlight(match_idx), x.group(0), right_highlight()), line_out, flags=re.IGNORECASE)
            if found_this_line >= matches_needed:
                if max_overall and found_overall == max_overall:
                    print("Found maximum overall", max_overall)
                    return found_so_far
                if max_in_file and found_so_far == max_in_file:
                    print("Found maximum per file", max_in_file)
                    return found_so_far
                if not found_so_far:
                    mt.print_centralized('{}{} {} found matches {}{}'.format(color_ary[header_color - 1] if header_color else '', hdr_equals, bf, hdr_equals, colorama.Style.RESET_ALL if header_color else ''))
                found_so_far += 1
                found_overall += 1
                print("    ({:5d}):".format(line_count), line_out, "{} L{}".format(current_table, current_table_line) if current_table else "")
                if post_open_matches:
                    mt.add_postopen(projfile, line_count)
    if verbose and not found_so_far:
        print("Nothing found in", projfile)
    return found_so_far

def related_projects(my_proj):
    cur_proj = ""

    for x in i7.i7com:
        if my_proj == x:
            if cur_proj:
                print("WARNING, redefinition of project-umbrella for", myproj)
            print("Forcing umbrella project", x)
            cur_proj = x
            break
        if my_proj in i7.i7com[x].split(","):
            if cur_proj:
                if i7.i7com[x] == i7.i7com[x]:
                    continue
                else:
                    print("WARNING, redefinition of project-umbrella for", myproj)
            cur_proj = x
    try:
        return i7.i7com[cur_proj].split(",")
    except:
        return [my_proj]

def read_args(my_arg_array):
    cmd_count = 0
    global verbose
    global user_input
    global post_open_matches
    global all_similar_projects
    global max_in_file
    global max_overall
    global view_history
    global verbose
    global quote_status
    global create_new_history
    global modify_line
    global include_notes
    global fast_match
    global match_string_array
    global my_proj
    while cmd_count < len(my_arg_array):
        arg = mt.nohy(my_arg_array[cmd_count])
        arg_orig = my_arg_array[cmd_count]
        if arg_orig in i7.i7x:
            my_proj = i7.i7x[arg_orig]
        elif arg_orig in i7.i7xr: # this is because we may have a dash- flag going to the same as a project name, so let's have a way to look at any project
            my_proj = arg_orig
        elif arg == 'r':
            print("Using super-shortcut 'r' for A Roiling Original.")
            my_proj = "roiling"
        elif arg == 'npo' or arg == 'pon':
            post_open_matches = False
        elif arg == 'po':
            post_open_matches = True
        elif arg == 'o':
            all_similar_projects = False
        elif arg == 'a':
            all_similar_projects = True
        elif arg[:2] == 'mf' and arg[2:].isdigit():
            max_in_file = int(arg[2:])
        elif arg[:2] == 'mo' and arg[2:].isdigit():
            max_overall = int(arg[2:])
        elif arg == 'vh':
            view_history = True
        elif arg == 'v':
            verbose = True
        elif arg == 'q':
            verbose = False
        elif arg == 'con' or arg == 'onc':
            colors = False
        elif arg == 'coff' or arg == 'offc':
            colors = False
        elif arg == 'qo' or arg == 'oq':
            quote_status = OUTSIDE
        elif arg == 'qi' or arg == 'iq':
            quote_status = INSIDE
        elif arg == 'qa' or arg == 'aq':
            quote_status = ALL
        elif arg == 'newhist':
            create_new_history = True
        elif arg == 'e' or arg == 'ec' or arg == 'ce':
            mt.npo(my_cfg)
        elif arg == 'ml' or arg == 'lm':
            modify_line = True
        elif sorted(arg) == 'lmn': #no modify line
            modify_line = False
        elif arg[:2] == 'mn':
            try:
                user_specified_matches_needed = int(arg[2:])
                if user_specified_matches_needed < 1:
                    sys.exit("-mn must define a positive number.")
            except:
                print("mn needs a valid number after it.")
        elif arg == 'ny' or arg == 'yn':
            include_notes = True
        elif arg == 'nn':
            include_notes = False
        elif arg == 'fm':
            fast_match = True
        elif arg == 'nfm' or arg == 'fmn':
            fast_match = False
        elif arg == 'ui':
            user_input = True
        elif arg == '?':
            usage()
        else:
            if verbose:
                print("Adding searchable string", arg)
            arg = arg.replace('/', '[^a-z]*')
            arg = arg.replace('`', '')
            if '#' in arg:
                arg = arg.replace('#', '=')
            if '=' in arg:
                ary = arg.split('=')
                if len(ary) == 2:
                    match_string_array.append("({}|{})".format(ary[0], ary[0] + ary[1]))
                else:
                    temp_ary = []
                    for x in ary[1:]:
                        temp_ary.append(ary[0] + x)
                    match_string_array.append("({})".format('|'.join(temp_ary)))
                cmd_count += 1
                continue
            if '!' in arg:
                ary = arg.split('!')
                arg = "(?<!{} ){}".format('|'.join(ary[:-1]), ary[-1])
            if '~' in arg:
                ary = arg.split('~')
                arg = "{} (?!{})".format(ary[0], '|'.join(ary[1:]))
            match_string_array.append(arg + '(s)?')
        cmd_count += 1

######################################main file below

read_cfg()

read_args(my_arg_array = sys.argv[1:])

if not my_proj:
    if not default_from_cwd:
        if not default_from_cfg:
            sys.exit("Must be in a project directory or specify a project.")
        if default_from_cfg in i7.i7x:
            my_proj = i7.i7x[default_from_cfg]
        print("Config file gives", my_proj, "as default project, so we'll use that, since the current directory isn't mapped to a valid project.")
    else:
        print("Using default project", default_from_cwd, "from current directory")
        my_proj = default_from_cwd

while first_loop or user_input:
    if user_input:
        frequencies.clear()
        from_user = input("search string (current project {}) >>".format(my_proj))
        if not from_user:
            sys.exit("Ok, that's all.")
        read_args(from_user.strip().split(" "))

    first_loop = False

    if all_similar_projects:
        proj_umbrella = related_projects(my_proj)
    else:
        proj_umbrella = [my_proj]

    history_file = hist_file_of(my_proj)

    if view_history:
        print(history_file)
        mt.npo(history_file)

    if not len(match_string_array):
        if user_input:
            print("OK, you may only have changed options. If you wish to exit, enter a blank line.")
            continue
        sys.exit("You need to specify text to find.")

    matches_needed = len(match_string_array)
    if user_specified_matches_needed:
        if user_specified_matches_needed > matches_needed:
            print("mn was bigger than the number of matches.")
        elif user_specified_matches_needed == matches_needed:
            print("mn was bigger than the number of matches.")
        else:
            matches_needed = user_specified_matches_needed

    print("Searching for string{}: {}".format(mt.plur(match_string_array), ' / '.join(match_string_array)))

    for proj in proj_umbrella:
        if proj not in i7.i7f:
            if os.path.exists(i7.main_src(proj)):
                print("No project exists for {}. But there is a story file. So I am using that.".format(proj))
                my_array = [ i7.main_src(proj) ]
            else:
                print("WARNING", proj, "does not have a project file array associated with it. It may not be a valid inform project.")
                continue
        else:
            my_array = i7.i7f[proj]
            if proj in i7.i7aux:
                my_array.extend(i7.i7aux[proj])
        for projfile in my_array:
            if not os.path.exists(projfile):
                if 'story.ni' in projfile:
                    print("Skipping nonexistent story file for {}, probably due to 'only' parameter.".format(proj))
                    continue
                print("Uh oh,", projfile, "does not exist. It probably should. Skipping.")
                continue
            if i7.inform_short_name(projfile) in frequencies:
                continue
            frequencies[i7.inform_short_name(projfile)] = find_text_in_file(match_string_array, projfile)
        notes_file = i7.notes_file(proj)
        if include_notes:
            if not os.path.exists(notes_file):
                print("Skipping absent notes file for", proj)
                continue
            if i7.inform_short_name(notes_file) in frequencies: # STS files overlap
                continue
            frequencies[i7.inform_short_name(notes_file)] = find_text_in_file(match_string_array, notes_file)
        elif os.path.exists(notes_file):
                print("Ignoring notes file {}. Toggle with yn/ny.".format(notes_file))
        notes_file = i7.notes_file(proj)

    if found_overall:
        print("    {}---- total matches printed: {}{}".format(colorama.Back.GREEN + colorama.Fore.BLACK, found_overall, colorama.Style.RESET_ALL))
        for x in sorted(frequencies, key=frequencies.get, reverse=True):
            if frequencies[x] < 1: continue
            print("    {}---- {} match{} in {}{}".format(colorama.Back.GREEN + colorama.Fore.BLACK, frequencies[x], 'es' if frequencies[x] > 1 else '', i7.inform_short_name(x), colorama.Back.BLACK))

        temp_array = [i7.inform_short_name(x) for x in frequencies if frequencies[x] == 0]
        if len(temp_array):
            my_join = ', '.join(temp_array).strip() # currently this creates extra red as there will probably be more than one line
            print("{}No matches for: {}".format(colorama.Back.RED + colorama.Fore.BLACK, my_join) + colorama.Back.BLACK)
            #print("{}No matches for: {}{}".format(colorama.Back.RED + colorama.Fore.BLACK, , colorama.Back.BLACK + colorama.Style.RESET_ALL))
    else:
        print("    {}---- NOTHING FOUND IN ANY FILES{}".format(colorama.Back.RED + colorama.Fore.BLACK, colorama.Style.RESET_ALL))

    temp_array = [i7.inform_short_name(x) for x in frequencies if frequencies[x] == -1]
    if len(temp_array):
        print("Left untested:", ', '.join(temp_array))
    write_history(history_file, ' '.join(sorted(match_string_array)), create_new_history)

    mt.post_open()
    match_string_array = []
