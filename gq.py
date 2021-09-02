# gq.py
#
# replaces gq.pl
#
# usage gq.py as match_string_raw (for alex smart)
#       gq.py `as                 (to search for the word AS, '/' = a bunch of non alpha words, '!' does negative lookbehind)
#       gq.py o shelf             (to search for shelf ONLY in the current project)
# this can use any number of words. It needs to find them all by default, but mn# specifices minimum matches needed, with some error checking
#
# note batch file shortcuts: gr tests STS, gs tests snooperism, ga tests Alec Smart
#
# to enable colors by default: REG ADD HKCU\CONSOLE /f /v VirtualTerminalLevel /t REG_DWORD /d 1
# I'd assume deleting this or changing it to zero would disable colors
#
# todo: print out duplicates vs actual count, determine which is relevant
# todo (stretch): if we have / in a line, look at individual slashes ... but ONLY if it is a notes file

from collections import defaultdict
import mytools as mt
import re
import i7
import sys
import os
import colorama
import codecs
import glob
from pathlib import Path

# variables potentially in CFG file

max_overall = 100
max_in_file = 25
history_max = 100
colors = True
fast_match = True
all_similar_projects = True
my_proj = ""
write_history = True
main_suffixes = 'er,ing,s,es,ies,tion,ity,ant,ment,ism,age,ery'
search_to_proc = False

verbose = False
quiet_procedural_notes = False

proc_dirs = [ "c:/writing/daily/to-proc" ]
proc_globs = [ "202*.txt" ]
most_recent_daily = True

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
post_open_warnings = True
hide_results = False

include_notes = True

modify_line = True

section_maps = defaultdict(list)
dgrab_latest_prompt = defaultdict(bool)
dgrab_general_prompt = defaultdict(bool)
congruences = defaultdict(lambda:defaultdict(str))

ALL=0
INSIDE=1
OUTSIDE=2

quote_status = ALL

user_specified_matches_needed = 0

# Keep this false or you may overwrite something
create_new_history = False

# variables not in CFG file/cmd line

first_loop = True

frequencies = defaultdict(int)
match_duplicates = defaultdict(int)

match_string_raw = []
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
    print("    !~ can also use \b if you want to demarcate word boundaries. More than one word = ! ORs all but last, ~ ORs all but first. pon=y=ies searches for pony or ponies. # allows different words altogether.")
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
    sys.exit()

def left_highlight(color_idx):
    return f'{color_ary[color_idx % len(color_ary)]}{highlight_types[my_highlight][0] * highlight_repeat}'

def right_highlight():
    return f'{highlight_types[my_highlight][1] * highlight_repeat}{colorama.Style.RESET_ALL}'

def hist_file_of(my_proj):
    return os.path.normpath(os.path.join("c:/writing/scripts/gqfiles", "gq-{}.txt".format(i7.combo_of(my_proj))))

def match_similar_words(my_line, my_dict):
    for d in my_dict:
        my_line = my_line.replace(d, my_dict[d])
    return my_line

def fast_string_of(my_regex):
    my_regex = my_regex.replace("(')?", "")
    for x in range(0, len(my_regex) - 1):
        if my_regex[x].isalpha and my_regex[x+1].isalpha:
            new_word = my_regex[x:]
            new_word = re.sub(r"[^a-z].*", "", new_word, flags=re.IGNORECASE)
            return new_word
    return "NOTHING_FOUND"

def match_string_of(my_regex):
    my_regex = my_regex.replace('/', '.*?')
    return r'\b{}\b'.format(my_regex)

def update_history_file(my_file, my_query, create_new_history = False):
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
        if not quiet_procedural_notes:
            print("Not rewriting since {} is already the first element.".format(my_query))
        return
    if my_query in ary:
        if not quiet_procedural_notes:
            print(my_query, "already in history.")
        ary.remove(my_query)
    ary.insert(0, my_query)
    if len(ary) > history_max:
        if not quiet_procedural_notes:
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
                if prefix == 'all_similar_projects':
                    global all_similar_projects
                    all_similar_projects = mt.truth_state_of(data)
                elif prefix == 'colors':
                    global colors
                    colors = mt.truth_state_of(data)
                elif prefix == 'congruences':
                    temp = data.split(';')
                    for t in temp:
                        ary = t.split('=')
                        for t2 in ary[1].split(','):
                            t3 = t2.split('/')
                            congruences[ary[0]][t3[0]] = t3[1]
                elif prefix == 'default_from_cfg':
                    global default_from_cfg
                    default_from_cfg = data
                elif prefix == 'fast_match':
                    global fast_match
                    fast_match = mt.truth_state_of(data)
                elif prefix in ( 'history', 'write_history' ):
                    global write_history
                    write_history = mt.truth_state_of(data)
                elif prefix == 'max_overall':
                    global max_overall
                    max_overall = int(data)
                elif prefix == 'min_overall':
                    global min_overall
                    min_overall = int(data)
                elif prefix == 'most_recent_daily':
                    global most_recent_daily
                    most_recent_daily = mt.truth_state_of(data)
                elif prefix == 'proc_dirs':
                    global proc_dirs
                    proc_dirs = [ os.path.normpath(x) for x in data.split(',') ]
                elif prefix == 'proc_globs':
                    global proc_globs
                    proc_globs = [ os.path.normpath(x) for x in data.split(',') ]
                elif prefix == 'search_to_proc':
                    global search_to_proc
                    search_to_proc = mt.truth_state_of(data)
                elif prefix == 'section_maps':
                    temp = data.split(';')
                    for x in temp:
                        temp2 = x.split('=')
                        section_maps[temp2[0]] = temp2[1].split(',')
                elif prefix in ( 'suffix', 'suffixes' ):
                    global main_suffixes
                    main_suffixes = data
                elif prefix == 'verbose':
                    global verbose
                    verbose = mt.truth_state_of(data)
                elif prefix == 'quiet':
                    global quiet_procedural_notes
                    quiet_procedural_notes = mt.truth_state_of(data)
                else:
                    print("Unknown = reading CFG, line", line_count, line.strip())

def find_text_in_file(match_string_raw, projfile, header_needed = []):
    should_search_header = len(header_needed) > 0
    if should_search_header and not projfile.endswith(".txt"):
        return -1
    if mt.is_daily(projfile) and not should_search_header:
        return -1
    fast_string_array = [ fast_string_of(x) for x in match_string_raw ]
    match_string_array = [ match_string_of(x) for x in match_string_raw ]
    global found_overall
    global overall_nonduplicate
    bf = i7.inform_short_name(projfile)
    if found_overall == max_overall:
        return -1
    found_so_far = 0
    local_nonduplicate = 0
    current_table = ""
    current_table_line = 0
    pbase = os.path.basename(projfile)
    current_daily_section = ''
    with codecs.open(projfile, encoding='utf8', errors='replace') as file:
        for (line_count, line) in enumerate (file, 1):
            if should_search_header:
                if not line:
                    current_daily_section = ''
                    continue
                elif line.startswith("\\"):
                    current_daily_section = line[1:].lower().strip()
                    continue
                elif current_daily_section not in header_needed:
                    continue
            if chr(65533) in line:
                print("WARNING line {} of {} had a character or characters unmappable in UTF-8, likely ellipses.".format(line_count, pbase))
                if post_open_warnings:
                    mt.add_postopen(projfile, line_count, priority = 12) # this is something we want to fix ASAP, so any post_open_matches can wait a minute.
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
            line_out = line.strip().lower()
            line_out_noap = line_out.replace("'", "")
            found_this_line = 0
            for match_idx in range(0, len(match_string_array)):
                if fast_match and fast_string_array[match_idx] not in line_out.noap:
                    continue
                if re.search(match_string_array[match_idx], line_out, flags=re.IGNORECASE):
                    found_this_line += 1
                    if modify_line:
                        line_out = re.sub(match_string_array[match_idx], lambda x: "{}{}{}".format(left_highlight(match_idx), x.group(0), right_highlight()), line_out, flags=re.IGNORECASE)
            if found_this_line >= matches_needed:
                if max_overall and found_overall == max_overall:
                    mt.print_centralized('{}Found maximum overall at {}: {}. Increase with -mo#.{}'.format(colorama.Back.WHITE + colorama.Fore.CYAN, pbase, max_overall, colorama.Style.RESET_ALL + colorama.Back.BLACK))
                    return found_so_far
                if max_in_file and found_so_far == max_in_file:
                    mt.print_centralized('{}Found maximum per file for {}: {}. Increase with -mf#.{}'.format(colorama.Back.WHITE + colorama.Fore.CYAN, pbase, max_in_file, colorama.Style.RESET_ALL + colorama.Back.BLACK))
                    return found_so_far
                if not found_so_far:
                    mt.print_centralized('{}{} {} found matches {}{}'.format(color_ary[header_color - 1] if header_color else '', hdr_equals, bf, hdr_equals, colorama.Style.RESET_ALL if header_color else ''))
                found_so_far += 1
                found_overall += 1
                sanitized_line = mt.strip_punctuation(line, remove_comments = True)
                if len(congruences[my_proj]):
                    sanitized_line = match_similar_words(sanitized_line, congruences[my_proj])
                is_duplicate = sanitized_line in match_duplicates
                if not is_duplicate:
                    local_nonduplicate += 1
                    overall_nonduplicate += 1
                    print("    ({:5d}):".format(line_count), line_out, "{} L{}".format(current_table, current_table_line) if current_table else "")
                    match_duplicates[sanitized_line] = "{} {}".format(pbase, line_count)
                    if current_daily_section:
                        if 'current' in i7.inform_short_name(projfile):
                            dgrab_latest_prompt[current_daily_section] = True
                        else:
                            dgrab_general_prompt[current_daily_section] = True
                else:
                    print(colorama.Back.RED + "    ({:5d}) DUPLICATE {}:".format(line_count, match_duplicates[sanitized_line]) + colorama.Style.RESET_ALL, line_out, "{} L{}".format(current_table, current_table_line) if current_table else "")
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

def read_args(my_arg_array, in_loop = False):
    cmd_count = 0
    global verbose
    global user_input
    global post_open_matches
    global post_open_warnings
    global all_similar_projects
    global max_in_file
    global max_overall
    global view_history
    global verbose
    global quiet_procedural_notes
    global quote_status
    global create_new_history
    global modify_line
    global include_notes
    global fast_match
    global match_string_raw
    global my_proj
    global hide_results
    global search_to_proc
    while cmd_count < len(my_arg_array):
        arg = mt.nohy(my_arg_array[cmd_count])
        arg_orig = my_arg_array[cmd_count].lower()
        if arg_orig in i7.i7x:
            my_proj = i7.i7x[arg_orig]
        elif arg_orig in i7.i7xr: # this is because we may have a dash- flag going to the same as a project name, so let's have a way to look at any project
            my_proj = arg_orig
        elif arg == 'r':
            print("Using super-shortcut 'r' for A Roiling Original.")
            my_proj = "roiling"
        elif arg in ( 'npo', 'pon' ):
            post_open_matches = False
        elif arg == 'po':
            post_open_matches = True
        elif arg in ( 'nw', 'wn'): # NOW or OWN or so forth are actual words, hence why it's different from above.
            post_open_warnings = False
        elif arg in ( 'ow', 'wo'):
            post_open_warnings = True
        elif arg in ( 'o', '.' ):
            all_similar_projects = False
        elif arg == 'a':
            all_similar_projects = True
        elif arg[:2] == 'mf' and arg[2:].isdigit():
            max_in_file = int(arg[2:])
        elif arg == 'mf':
            try:
                max_in_file = int(my_arg_array[cmd_count + 1])
                print("Trivial warning: mf and a number don't need a space between them.")
                cmd_count += 1
            except:
                sys.exit("MF needs a number after it.")
        elif arg[:2] == 'mo' and arg[2:].isdigit():
            max_overall = int(arg[2:])
        elif arg == 'mo':
            try:
                max_overall = int(my_arg_array[cmd_count + 1])
                print("Trivial warning: mo and a number don't need a space between them.")
                cmd_count += 1
            except:
                sys.exit("MO needs a number after it.")
        elif arg == 'hr':
            hide_results = True
        elif arg == 'vh':
            view_history = True
        elif arg == 'tp':
            search_to_proc = True
        elif arg == 'v':
            verbose = True
        elif arg == 'b':
            verbose = False
            quiet_procedural_notes = False
            hide_results = False
        elif arg == 'q':
            verbose = False
            quiet_procedural_notes = True
            hide_results = True
        elif arg in ( 'con', 'onc' ):
            colors = False
        elif arg in ( 'coff', 'offc' ):
            colors = False
        elif arg in ( 'wh', 'hw' ):
            write_history = True
        elif arg in ( 'nh', 'hn' ):
            write_history = False
        elif arg in ( 'qo', 'oq' ):
            quote_status = OUTSIDE
        elif arg in ( 'qi', 'iq' ):
            quote_status = INSIDE
        elif arg in ( 'qa', 'aq' ):
            quote_status = ALL
        elif arg == 'newhist':
            create_new_history = True
        elif arg in ( 'e', 'ec', 'ce' ):
            mt.npo(my_cfg)
        elif arg in ( 'ml', 'lm' ):
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
        elif arg in ( 'ny', 'yn' ):
            include_notes = True
        elif arg == 'nn':
            include_notes = False
        elif arg == 'fm':
            fast_match = True
        elif arg in ( 'nfm', 'fmn' ):
            fast_match = False
        elif arg in ( 'ui', 'in' ):
            user_input = True
        elif 'gq' in arg and "`" not in arg:
            mt.print_centralized(colorama.Back.RED + colorama.Fore.BLACK + "WARNING gq argument in user input. Use backtick to not ignore." + colorama.Back.BLACK + colorama.Style.RESET_ALL)
        elif arg.endswith(".py") or arg.endswith(".pl"):
            return_value = -1
        elif arg == '?':
            usage()
        else:
            add_plural_suffix = True
            if verbose:
                print("Adding searchable string", arg)
            if arg.startswith("?"):
                arg = arg[1:]
                print("Finding definition for", arg)
                os.system("start http://www.thefreedictionary.com/{}".format(arg))
            temp_replace = '{}[^a-z]*'.format('' if arg.endswith('/') else '(s)?')
            if arg.endswith('/'):
                arg = arg[:-1]
                add_plural_suffix = False
            arg = arg.replace('/', temp_replace, arg.count('/') - (arg[-1] == '/')) # possible separate words with no other text between them
            arg = arg.replace('`', '')
            if "'" in arg: # optional apostrophes E.g. Yall or Y'all
                arg = arg.replace("'", "(')?")
            if arg.endswith('#'): # ending with pound sign adds the main suffixes to a word
                match_string_raw.append("{}({})?".format(arg[:-1], '|'.join(main_suffixes.split(','))))
                cmd_count += 1
                continue
            if '#' in arg: # multiple possibilities after a word chunk e.g. cand#y#ies#idate
                ary = arg.split('#')
                match_string_raw.append("{}({})?".format(ary[0], '|'.join(ary[1:])))
                cmd_count += 1
                continue
            if '=' in arg: # multiple possibilities after a word chunk e.g. cand=y=ies=idate but don't want the base word
                ary = arg.split('=')
                if len(ary) == 2:
                    match_string_raw.append("({}|{})".format(ary[0], ary[0] + ary[1]))
                else:
                    temp_ary = []
                    for x in ary[1:]:
                        temp_ary.append(ary[0] + x)
                    match_string_raw.append("({})".format('|'.join(temp_ary)))
                cmd_count += 1
                sys.exit(match_string_raw)
                continue
            if '!' in arg: # don't have most words behind last
                ary = arg.split('!')
                arg = "(?<!{} ){}".format('|'.join(ary[:-1]), ary[-1])
            if '~' in arg: # don't have 2nd+ words ahead of first
                ary = arg.split('~')
                arg = "{} (?!{})".format(ary[0], '|'.join(ary[1:]))
            match_string_raw.append(arg + ('(s)?' if add_plural_suffix else ''))
        cmd_count += 1
    return 0

######################################main file below

read_cfg()

error_check = read_args(my_arg_array = sys.argv[1:])

if not len(match_string_raw) and not user_input:
    print("I didn't register any text to search for. Perhaps some text is an option in the code. If so, you can start a parameter with backticks to make sure it is seen as text to search.")
    sys.exit()

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

daily_sections = section_maps[my_proj]

while first_loop or user_input:
    found_overall = 0
    overall_nonduplicate = 0
    frequencies.clear()

    if user_input:
        from_user = input("search string (current project {}) >>".format(my_proj))
        if not from_user:
            sys.exit("Ok, that's all.")
        error_check = read_args(from_user.strip().split(" "), in_loop = True)

    first_loop = False

    if all_similar_projects:
        proj_umbrella = related_projects(my_proj)
    else:
        proj_umbrella = [my_proj]

    history_file = hist_file_of(my_proj)

    if view_history:
        print(history_file)
        mt.npo(history_file)

    if not len(match_string_raw):
        if user_input:
            print("OK, you may only have changed options. If you wish to exit, enter a blank line.")
            continue
        sys.exit("You need to specify text to find.")

    matches_needed = len(match_string_raw)
    if user_specified_matches_needed:
        if user_specified_matches_needed > matches_needed:
            print("mn was bigger than the number of matches.")
        elif user_specified_matches_needed == matches_needed:
            print("mn was bigger than the number of matches.")
        else:
            matches_needed = user_specified_matches_needed

    if not quiet_procedural_notes:
        print("Searching for string{}: {}".format(mt.plur(match_string_raw), ' / '.join(match_string_raw)))

    for proj in proj_umbrella:
        if proj not in i7.i7f:
            if os.path.exists(i7.main_src(proj)):
                if not quiet_procedural_notes:
                    print("No project filemap exists for {}. But there is a story file. So I am using that.".format(proj))
                my_array = [ i7.main_src(proj) ]
            else:
                print("WARNING", proj, "does not have a project file array associated with it. It may not be a valid inform project.")
                continue
        else:
            my_array = i7.i7f[proj]
            if proj in i7.i7aux:
                my_array.extend(i7.i7aux[proj])
        my_array = [os.path.realpath(x) for x in my_array]
        for projfile in my_array:
            if projfile in frequencies:
                if not quiet_procedural_notes:
                    print(projfile, "or a symbolically linked file was already read. Skipping.")
                continue
            if not os.path.exists(projfile):
                if 'story.ni' in projfile:
                    if proj in i7.i7com:
                        print("Skipping nonexistent story file for umbrella project {}. We probably don't need one.".format(proj))
                    else:
                        print("Skipping nonexistent story file for {}. Maybe we should have one.".format(proj))
                    continue
                print("Uh oh,", projfile, "does not exist. It probably should. Skipping.")
                continue
            if i7.inform_short_name(projfile) in frequencies:
                continue
            frequencies[i7.inform_short_name(projfile)] = find_text_in_file(match_string_raw, projfile)
        notes_file = os.path.realpath(i7.notes_file(proj))
        if include_notes:
            if notes_file in frequencies:
                if not quiet_procedural_notes:
                    print(notes_file, "or a symbolically linked file was already read. Skipping.")
                continue
            if not os.path.exists(notes_file):
                if proj in i7.i7com:
                    print("Skipping absent combo-project notes file for {}. However, we are scanning individual project notes files.".format(proj))
                else:
                    print("Skipping absent combo-project notes file for {}. Maybe we should have one?".format(proj))
                continue
            if i7.inform_short_name(notes_file) in frequencies: # STS files overlap
                continue
            frequencies[i7.inform_short_name(notes_file)] = find_text_in_file(match_string_raw, notes_file)
        elif os.path.exists(notes_file):
                print("Ignoring notes file {}. Toggle with yn/ny.".format(notes_file))

    if search_to_proc:
        for x in proc_dirs:
            for y in proc_globs:
                for z in glob.glob(os.path.join(x, y)):
                    if not mt.is_daily(z):
                        continue
                    frequencies[z] = find_text_in_file(match_string_raw, z, header_needed = daily_sections)

        if most_recent_daily:
            for x in proc_dirs:
                all_files = []
                the_parent = Path(x).parent.absolute()
                all_files.extend(glob.glob(os.path.join(the_parent, y)))
                all_files = sorted(all_files)
                if len(all_files) == 0:
                    continue
                last_daily = all_files[-1]
                if os.path.exists(os.path.join(x, os.path.basename(last_daily))):
                    continue
                frequencies[last_daily] = find_text_in_file(match_string_raw, last_daily, header_needed = daily_sections)

    if hide_results:
       pass
    elif found_overall:
        print("    {}---- total matches printed: {}{}".format(colorama.Back.GREEN + colorama.Fore.BLACK, found_overall, colorama.Style.RESET_ALL))
        for x in sorted(frequencies, key=frequencies.get, reverse=True):
            if frequencies[x] < 1: continue
            print("    {}---- {} match{} in {}{}".format(colorama.Back.GREEN + colorama.Fore.BLACK, frequencies[x], 'es' if frequencies[x] > 1 else '', i7.inform_short_name(x), colorama.Back.BLACK + colorama.Style.RESET_ALL))

        temp_array = [i7.inform_short_name(x) for x in frequencies if frequencies[x] == 0 and not mt.is_daily(x)]
        if len(temp_array):
            my_join = ', '.join(temp_array).strip() # currently this creates extra red as there will probably be more than one line
            print("{}No matches for: {}".format(colorama.Back.RED + colorama.Fore.BLACK, my_join) + colorama.Back.BLACK + colorama.Style.RESET_ALL)
            #print("{}No matches for: {}{}".format(colorama.Back.RED + colorama.Fore.BLACK, , colorama.Back.BLACK + colorama.Style.RESET_ALL))
        if len(dgrab_latest_prompt) or len(dgrab_general_prompt):
            print(colorama.Back.MAGENTA + "Some stuff should be shifted from daily files. Use these commands:" + colorama.Style.RESET_ALL)
        for dp in dgrab_general_prompt:
            print(colorama.Back.MAGENTA + "      dgrab.py s={}".format(dp) + colorama.Style.RESET_ALL)
        for dp in dgrab_latest_prompt:
            print(colorama.Back.MAGENTA + "      dgrab.py ld s={}".format(dp) + colorama.Style.RESET_ALL)
    else:
        print("    {}---- NOTHING FOUND IN ANY FILES{}".format(colorama.Back.RED + colorama.Fore.BLACK, colorama.Back.BLACK + colorama.Style.RESET_ALL))
        print("    " + ", ".join(frequencies))

    temp_array = [i7.inform_short_name(x) for x in frequencies if frequencies[x] == -1 and not mt.is_daily(x)]
    if len(temp_array):
        print("Left untested:", ', '.join(temp_array))

    if write_history:
        update_history_file(history_file, ' '.join(sorted(match_string_raw)), create_new_history)

    mt.post_open(bail_after = False)
    match_string_raw = []
