# i7.py
#
# basic dictionaries for various projects
#
# along with very basic python functions
#
# dir2proj converts current directory to project
# in_quotes only gets text in quotes
# proj_exp = project expansion
#

import xml.etree.ElementTree as ET
from collections import defaultdict
import mytools as mt
import sys
import re
import os
import glob
from filecmp import cmp
from shutil import copy, move
import __main__ as main
import pathlib

# these are the main dicts used in the i7 modules
# some of these may have underscores due to how I named the release files
# e.g. shuffling -> shuffling_around
#
# I could create i7full but that would be arduous

# i7 defined arrays for both perl/python files
# read from i7p.txt/i7_cfg_file

i7gx = {} # github project renaming e.g. compound -> the_problems_compound. Most of the time this won't matter--GH = what's on my computer
i7gxr = {} # github project renaming reversed e.g. the_problems_compound -> compound. Most of the time this won't matter--GH = what's on my computer
i7x = {} # mapping abbreviation to main project e.g. ai = ailihphilia
i7xr = {} # mapping main project to unique/main abbreviation e.g. buck-the-past<=>btp but compound -> pc not 15 as pc is 1st
i7com = {} # combos e.g. opo = 3d and 4d
i7comr = {} # combos reversed
i7comord = defaultdict(lambda: defaultdict(int)) # ordered combos e.g. shuffling,roiling = 1,2 in stale tales slate
i7hfx = {} # header mappings e.g. ta to tables
i7f = {} # which program files (x86)\inform header files are included by which projects e.g. shuffling has Nudges,Random Text,Mistakes,Tables
i7fg = {} # which users\documents\github header files are included by which projects e.g. shuffling has Nudges,Random Text,Mistakes,Tables
i7rn = {} # release numbers
i7nonhdr = {} # non header files e.g. story.ni, walkthrough.txt, notes.txt
i7triz = {} # there may be trizbort file name shifts e.g. shuffling -> shuffling-around
i7trizmaps = defaultdict(lambda:defaultdict(str)) # trizbort map sub-naming, mainly for Roiling
i7aux = {} # general auxiliary files outside the general formulae for projects. Currently only spopal.otl,
i7gsn = {} # generic short names e.g. story.ni to source file
i7gbx = {} # general binary extensions for debug, beta and release e.g. z6 goes to z8 z5 z5
i7pbx = {} # project binary extensions for debug, beta and release
i7binname = {} # binary nams e.g. roiling to A Roiling Original

i7ignore = [] # "bad projects" or ones not seen any more, to be ignored in searching
i7bb = [] # list of bitbucket repos
i7gh = [] # list of github repos

######################################################default variables

auth = "Andrew Schultz"
ext_root = extroot = r'c:\Program Files (x86)\Inform 7\Inform7\Extensions'
ext_dir = extdir = os.path.join(extroot, auth) # NOTE: the x86 is right, here. No need or desire for mt.progfile.
nice = nz = nicez = os.path.join(extdir, "Trivial Niceties Z-Only.i7x")
niceg = ng = os.path.join(extdir, "Trivial Niceties.i7x")
tmp_hdr = temp_hdr = tmp_header = temp_header = os.path.join(extdir, "temp.i7x")
np = mt.np
npnq = mt.npnq
f_dic = "c:/writing/dict/brit-1word.txt"
f_f = "c:/writing/dict/firsts.txt"
f_l = "c:/writing/dict/lasts.txt"
prt = "c:/games/inform/prt"
prt_temp = os.path.join(prt, "temp")
i7_cfg_file = "c:/writing/scripts/i7p.txt"
i7_temp_config = "c:/writing/scripts/i7d.txt"
triz_dir = "c:\\games\\inform\\triz\\mine"
gh_dir = "c:\\users\\andrew\\documents\\GitHub"
beta_dir = "c:/games/inform/beta Materials/Release"
latest_project_abbr = latest_project_long = ''

# these are default values for binaries--debug is assumed to be most important
# since it is the one I'll be using the most.
# beta is used for automation.
UNSPECIFIED = -1 # in case we demand a value
DEBUG = 0
BETA = 1
RELEASE = 2

i7fi = { 'f': f_f, 'l': f_l, 'w': f_dic, 'b': f_dic }

table_row_count = defaultdict(int)

outline_val_hash = { 'volume': 5, 'book': 4, 'part': 3, 'chapter': 2, 'section': 1 }
ovh = outline_val_hash
outline_val = sorted(outline_val_hash, key=outline_val_hash.get)
ov = outline_val
outline_re = r'^({:s})'.format('|'.join(outline_val_hash))

on_off = [ 'off', 'on' ]
oo = on_off

smart = "c:/writing/smart.otl"
spoon = "c:/writing/spopal.otl"

def is_main_abb(x):
    return x == main_abb(x)

def strip_name_punc(x, remove_apostrophe = True, space_dash = True):
    temp = x
    if space_dash:
        temp = temp.replace('-', ' ')
    if remove_apostrophe:
        temp = temp.replace("'", '')
    return temp

strip_name = name_strip = strip_name_punc

def long_name(x, debug = False, strip_dashes = False, use_given = False):
    if x in i7x:
        temp = i7x[x]
        if strip_dashes:
            temp = strip_name_punc(temp)
        return temp
    if x in i7xr:
        return x
    if debug:
        print("Warning: finding long name for", x," failed.")
    if not use_given:
        return ''
    return x

def main_abb(x, use_given = False):
    if x in i7xr:
        return i7xr[x]
    if x not in i7x:
        if use_given:
            return x
        return ""
    if i7x[x] not in i7xr:
        print("    **** I7.PY WARNING {}/{} does not have reverse abbreviation.".format(x, i7x[x]))
        return ""
    return i7xr[i7x[x]]

main_abbr = main_abbrev = main_abb

def dict_val_or_similar(my_key, my_dict):
    if my_key in my_dict:
        return my_dict[my_key]
    if my_key in i7xr and i7xr[my_key] in my_dict:
        return my_dict[i7xr[my_key]]
    if my_key in i7x and i7x[my_key] in my_dict:
        return my_dict[i7x[my_key]]
    if main_abb(my_key) in my_dict:
        return my_dict[main_abb(my_key)]
    return my_key

dictish = dict_val_or_similar

def in_dict_or_abbrev(my_key, my_dict):
    if my_key in my_dict:
        return True
    if my_key in i7xr and i7xr[my_key] in my_dict:
        return True
    if my_key in i7x and i7x[my_key] in my_dict:
        return True
    if main_abb(my_key) in my_dict:
        return True
    return False

inish = in_dict_or_abbrev

def apostrophe_to_quotes(x):
    temp = re.sub(" '", ' "', x)
    temp = re.sub("' ", '" ', temp)
    temp = re.sub(r"('$|^')", '"', temp)
    return re.sub("\['\]", "'", temp)
    #temp = re.sub(r'(\b'|'\b|'$|^')', '"', x)
    return temp

a2q = apostrophe_to_quotes

def to_table(x):
    return re.sub(" *\[.*", "", line.lower().strip())

def is_outline_start(x, case_insensitive = True):
    return re.sub(outline_re, x)

oline = is_outline_start

def zap_end_brax(x):
    x = x.strip()
    while x.endswith("]"):
        x = re.sub(" *\[.*?\]", "", x)
    return x

def first_table_text(my_line, include_quotes = False):
    ary = my_line.strip().split("\t")
    for x in ary:
        if x.startswith('"'):
            retval = x.split('"')[1]
            if include_quotes:
                retval = '"' + retval + '"'
            return retval
    return ''

def cols_of(file_name, table_name, default_value = 0, warn_if_different = True):
    if not os.path.exists(file_name):
        print("Going with default value {} for {} # of columns as {} doesn't exist.".format(default_value, table_name, file_name))
        return default_value
    check_next = False
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.lower().startswith(table_name.lower()):
                check_next = True
                continue
            if check_next:
                line = re.sub("[ \t]*\[[^\]]*\]", "", line)
                ret_val = len(line.split("\t"))
                if default_value and warn_if_different and default_value != ret_val:
                    print("WARNING: return value {} different from default value {}.".format(ret_val, default_value))
                return ret_val
    print("Did not find table name {} in {}. Returning default value {} for # of columns.".format(table_name, file_name, default_value))
    return default_value

def column_from_header_line(x, line, file_name = "", file_line = 0):
    line = line.strip()
    ary = [mt.zap_trail_paren(temp).lower() for temp in line.lower().split("\t")]
    xl = x.lower()
    try:
        return ary.index(xl)
    except:
        sys.exit("Tried to find the element <<{}>> in the tab-delimited line <<{}>>{}{}but failed. Bailing.".format(xl, line.lower().strip().replace("\t", " / "), "" if not file_name else " " + file_name, "" if not file_line else " line {}".format(file_line) ))

def mult_columns_from_header_line(col_array, line, file_name = "", file_line = 0):
    for q in col_array:
        yield column_from_header_line(q, line, file_name = "", file_line = 0)

def column_from_file(file_name, table_name, column_name):
    got_any = False
    next_header = False
    if not table_name.startswith("table of "):
        table_name = "table of " + table_name
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(table_name) and "\t" not in line:
                got_any = True
                next_header = True
                continue
            if next_header:
                if type(column_name) == list: return mult_columns_from_header_line(column_name, line, file_name, line_count)
                return column_from_header_line(column_name, line, file_name, line_count)
    if not got_any:
        sys.exit("Could not find table <<>> in <<>> to read columns. Bailing.".format(table_name, file_name))

mult_columns_from_header_file = column_from_file

def i7_text_convert(my_string, erase_brackets = True, bracket_replace = '/', ignore_array = [], color_punc_change = False):
    #temp = re.sub(r"'(?![\]a-z])", '"', my_string, flags=re.IGNORECASE)
    #temp = re.sub(r"(?<![\[a-z])'", '"', temp, flags=re.IGNORECASE)
    iglo = [x.lower() for x in ignore_array]
    temp = my_string.replace("[']", mt.green_of("'", color_punc_change))
    temp = re.sub(r"([!.])'", r'\1' + mt.green_of(r'"', color_punc_change), temp)
    if erase_brackets:
        temp = re.sub("\[[^\]]*\]", bracket_replace, temp)
    for x in re.findall(r"[a-zA-Z]+'(?![\]a-zA-Z])", temp):
        if x.lower() not in iglo:
            temp = re.sub(x, x.replace("'", (mt.green_of('"', color_punc_change))), temp)
            temp = re.sub(r"{}(?![\]a-zA-Z])".format(x), x.replace('"', "'"), temp)
    for x in re.findall(r"(?<![\[A-Za-z])'[a-zA-Z]+", temp):
        if x.lower() not in iglo:
            temp = re.sub(x, x.replace("'", (mt.green_of('"', color_punc_change))), temp)
            temp = re.sub(r"(?<![\[A-Za-z]){}".format(x), x.replace('"', "'"), temp)
    return temp

text_convert = i7_text_convert

#print(text_convert("'This is a test of my Inform single-quote conversion function. It's got seven test cases,' said Andrew, avoiding 'air quotes' because those annoy everyone. 'Folks['] opinions may vary on if this is a good test string, but it's the best I could do. The final case is the end quote.'"))

def quoted_text_array_of(my_line, erase_brackets = True, get_inside = True, as_list = True, bracket_replace = '/'):
    temp = text_convert(my_line, erase_brackets = erase_brackets, bracket_replace = bracket_replace)
    ary = temp.split('"')[get_inside::2]
    if as_list:
        return ary
    else:
        return ' '.join(ary)

def one_topic_to_array(x, div_char = "/"): # a/b c/d to a c, a d,
    if div_char not in ''.join(x):
        return [x]
    return_array = []
    for y in range(0, len(x)):
        if div_char in x[y]:
            for z in x[y].split(div_char):
                new_array = list(x)
                new_array.pop(y)
                new_array.insert(y, z)
                temp = one_topic_to_array(new_array)
                return_array.extend(temp)
            return return_array
    return return_array

def topics_to_array(x, div_char = "/", convert_to_spaces = True, double_dash_to_blank = True):
    ret_ary = []
    if '"' in x:
        all_topics = x.split('"')
    else:
        all_topics = [x]
    for temp in all_topics[1::2]:
        if double_dash_to_blank:
            temp = re.sub("\w--\w", "", temp)
        temp2 = one_topic_to_array(temp.split(' '))
        ret_ary.extend(temp2)
    if convert_to_spaces:
        return [ ' '.join(x) for x in ret_ary ]
    return ret_ary

topx2ary = topics_to_array

def is_beta_include(this_line):
    tll = this_line.lower()
    return tll.startswith("include") and " beta" in tll

def create_beta_source(my_proj, beta_proj = "beta", text_to_find = "beta testing"):
    got_beta_line = False
    changed_beta_line = False
    from_file = main_src(my_proj)
    to_file = main_src(beta_proj)
    f = open(to_file, "w", newline="\n")
    with open(from_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if re.search("^(volume|book|part|chapter|section) {}".format(text_to_find), line.lower()):
                got_beta_line = True
                if "not for release" in line:
                    changed_beta_line = True
                    line = line.replace('not for release', '').strip()
                    line = re.sub("-$", "", line).strip()
                    f.write(line + '\n')
                    continue
                else:
                    print("Found beta line {}, but it was already marked for-release.".format(line.strip()))
            elif is_beta_include(line):
                line = line.replace('[', '').replace(']', '')
                got_beta_line = True
            f.write(line)
    f.close()
    if not got_beta_line:
        print("WARNIING: Found no '{}' line in {}, returning.".format(text_to_find, from_file))
        os.remove(to_file)
        return
    if not changed_beta_line:
        print("Did not change '{}' line in {}, returning.".format(text_to_find, from_file))
        os.remove(to_file)
        return
    print("Successfully toggled '{}' line in {} to {}".format(text_to_find, my_proj, beta_proj))

def qfi(x, base_only = True):
    if x in i7fi.keys(): return os.path.basename(i7fi[x]) if base_only else i7fi[x]
    return x

def ph(eqs, opt_text = ""):
    print('=' * eqs + opt_text)

def i7_usage():
    print("proj_exp = main function, short name to long. dir2proj = directory to project.")
    print("mifi tefi tafi = mistake test table files")
    exit()

def is_outline_start(a):
    ovr = r'^({:s}) '.format("|".join(outline_val_hash))
    if re.search(ovr, a.lower()): return re.sub(" .*", "", a.lower())
    return ""

def outline_indent(a):
    for x in outline_val_hash:
        if a.lower().startswith(x):
            return '  ' * outline_val_hash[x]
    return ''

def outline_type(a):
    return re.sub(" .*", "", a.strip().lower())

def no_lead_art(x):
    return re.sub("^(some|the|an|a) (thing called )?", "", x, 0, re.IGNORECASE)

def words_file(x):
    if type(x) == str: return "c:/writing/dict/words-{:d}.txt".format(x)
    if x.isdigit():
        x2 = int(x)
        return "c:/writing/dict/words-{:d}.txt".format(x)
    print ("Words_file call needs integer or string-like integer.")
    return "c:/writing/dict/words-0.txt"

w_f = words_file

def in_quotes(x, get_second=True, get_comments=False):
    j = x.split('"')[get_second::2]
    retval = ' '.join(j)
    if not get_comments: retval = re.sub("\[[\]]*\]", "", retval)
    return retval

def new_lev(x):
    for j in range (0, len(ov)):
        if x.lower().startswith(ov[j]): return j+1
    return 0

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def file_len_eq(f1, f2, bail = True, launch = False):
    fl1 = file_len(f1)
    fl2 = file_len(f2)
    if fl1 != fl2:
        oops_string = "{:s} and {:s} have different # of lines, suggesting corrupt data: {:d} vs {:d}.".format(f1, f2, fl1, fl2)
        if launch: wm(f1, f2)
        if bail:
            sys.exit(oops_string)
        else:
            print(oops_string)
        return False
    return True

def audit_table_rows(file_name, ignore_trivial = True, ignore_specific = [], ignore_glob = [], only_glob = [], show_params = False, parse_string_parameters = True, open_after_priority = 10):
    if type(ignore_specific) == str:
        ignore_specific = ignore_specific.split(",") if parse_string_parameters else [ignore_specific]
    if type(ignore_glob) == str:
        ignore_glob = ignore_glob.split(",") if parse_string_parameters else [ignore_glob]
    if type(only_glob) == str:
        only_glob = only_glob.split(",") if parse_string_parameters else [only_glob]
    trivials = ['trivially true rule', 'trivially false rule']
    rule_dict = defaultdict(int)
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if "this is the" in line:
                if re.search("this is the .* rule", line):
                    my_rule = re.sub(r'.*this is the +(.*?) +rule.*', r'\1 rule', line.strip())
                    if my_rule in rule_dict:
                        print("Duplicate rule dict {} at line {}.".format(my_rule, line_count))
                    else:
                       rule_dict[my_rule] = line_count
    with open(file_name) as file:
        for (line_count, line) in enumerate(file):
            if ' rule' not in line: continue
            if "\t" in line.strip():
                mb_rules = line.strip().split("\t")
                for q in mb_rules:
                    if ' rule' not in q or '"' in q: continue
                    if q in rule_dict:
                        rule_dict.pop(q)
            x = re.sub('(consider|process|follow|abide by) the (.*?) rule.*', '\1 rule', line.strip())
            if x in rule_dict:
                rule_dict.delete(x)
    if only_glob:
        for g in only_glob:
            for t in list(rule_dict.keys()):
                if not re.search(g, t):
                    rule_dict.pop(t)
    if ignore_trivial:
        for t in trivials:
            if t in rule_dict:
                rule_dict.pop(t)
    if len(ignore_specific):
        for t in ignore_specific:
            if t in rule_dict:
                rule_dict.pop(t)
    if len(ignore_glob):
        for g in ignore_glob:
            for t in list(rule_dict.keys()):
                if re.search(g, t):
                    rule_dict.pop(t)
    lrd = len(rule_dict)
    if lrd:
        print( "{} rule{} were found in the source but not in a table.".format(lrd, mt.plur(lrd)))
        for q in rule_dict:
            print(q, rule_dict[q])
    else:
        print("All tables match for {}.".format(os.path.basename(file_name)))
    if show_params:
        print("Ignore trivial={}, ignore_specific={}, ignore_glob={}".format(ignore_trivial, ignore_specific, ignore_glob))
    if open_after_priority and len(rule_dict):
        mt.add_postopen_file_line(file_name, min(rule_dict.values()), priority=open_after_priority)
    return lrd

def get_table_row_count(q, clear_trc = False, show_detail = False, lower_case = True, bail_on_dupe = False):
    if clear_trc: table_row_count.clear()
    table_start = 0
    table_name = ''
    if os.path.exists(q): # it's a file
        if show_detail: print("Reading", q)
        with open(q) as file:
            for (line_count, line) in enumerate(file, 1):
                if line.startswith('table'):
                    table_name = re.sub(" \[.*", "", line.strip())
                    if table_name in table_row_count.keys():
                        my_msg = "Duplicate table name found: {:s}, {:s}, line {:d}".format(table_name, q, line_count)
                        if bail_on_dupe: sys.exit(my_msg)
                        print("WARNING:", my_msg)
                    if lower_case: table_name = table_name.lower()
                    table_start = line_count + 2
                if not line.strip():
                    if table_name:
                        table_row_count[table_name] = line_count - table_start
                        if show_detail: print(table_name, table_row_count)
    elif proj_exp(q, False):
        for q2 in i7f[proj_exp(q, False)]:
            get_table_row_count(q2, show_detail = show_detail)
    else:
        print("No project or file", q)

get_trc = get_table_row_count

o_s = open_source = mt.open_source

oc = o_c = open_config = open_source_config = mt.open_source_config

# to python regression test
def to_prt(include_glob = "reg-*", exclude_glob = ""):
    j = glob.glob(include_glob)
    xg = '(no exclude)' if not exclude_glob else exclude_glob
    for j1 in j:
        if re.search(exclude_glob, j):
            uncopied += 1
            continue
        prt_out = os.path.join(prt, os.path.basename(j1))
        if not cmp(j1, prt_out):
            copy(j1, prt_out)
            copied += 1
    print(copied, "copied of ", include_glob, "-", xg, ",", uncopied, "uncopied")

#for backwards compatibility. wm and plur used to be in i7.
plur = mt.plur
wm = mt.wm

def remove_quotes(x):
    temp = re.sub("\"", "", x)
    temp = re.sub("\".*", "", x)
    return temp

rq = remove_quotes

def gh_src(x = os.getcwd(), give_source = True):
    temp = proj_exp(x, to_github = True)
    if temp in i7gx:
        temp = i7gx[temp]
    retval = os.path.join(gh_dir, temp)
    if give_source: retval = os.path.join(retval, "story.ni")
    return os.path.normpath(retval)

github_source = gh_source = github_src = gh_src

def i2g(x, force_copy_to_github = False, force_copy_from_github = False):
    if force_copy_to_github and force_copy_from_github:
        print("Whoah there little dude! You can't force copying to and from {:s}!".format(sys._getframe().f_code.co_name))
        return
    temp = main_src(x)
    t2 = gh_src(x)
    if os.path.islink(temp):
        tlink = os.readlink(temp)
        if tlink == t2:
            print(temp, "and", t2, "both match up.")
        else:
            sys.exit("Bad link {:s} points to {:s} but should point to {:s}.".format(temp, tlink, t2))
    if not os.path.exists(temp):
        print("No file", temp, "for project", x)
        return
    if force_copy_to_github:
        print("Copying over", temp, "to", t2)
        copy(temp, t2)
    elif force_copy_from_github:
        print("Copying over", t2, "to", temp)
        copy(t2, temp)
    else:
        print("Comparing", temp, "and", t2)
        print("... set force_copy to True in", sys._getframe().f_code.co_name, "to force copy")
        wm(temp, t2)

def blurb_file(x):
    return os.path.normpath(os.path.join(proj2root(x), "Release.blurb"))

blurb = blurb_file

def uid_file(x):
    return os.path.normpath(os.path.join(proj2root(x), "uuid.txt"))

uuid = uuid_file = uidfile = uid_file

def uuid_value(x):
    dummy_id = '00000000-0000-0000-0000-0000-00000000'
    if not os.path.exists(uidfile(x)):
        print("WARNING: could not find uuid file for project {x}. Going with default.")
        return dummy_id
    with open(uid_file(x)) as file:
        for line in file:
            l = line.strip()
            print(l)
            if re.search("^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$", l):
                return line
    print("WARNING: could not find valid UUID in uuid file for project {x}. Going with default.")
    return dummy_id

def auto_file(x):
    return os.path.normpath(os.path.join(proj2root(x), "auto.inf"))

def main_src(x = os.getcwd(), return_nonexistent = True):
    main_path = os.path.normpath(os.path.join(sdir(x), "story.ni"))
    if return_nonexistent or os.path.exists(main_path):
        return main_path
    return ""

proj_src = src = get_src = main_src

def src_file(x, y):
    if y in i7nonhdr.keys():
        return os.path.join(sdir(x), i7nonhdr[y])
    elif y in i7nonhdr.values():
        return os.path.join(sdir(x), y)
    if y in i7hfx.keys():
        return hdr(x, i7hfx[y].title())
    elif y in i7hfx.values():
        return hdr(x, y)
    return ""

def build_log(x):
    return os.path.normpath(os.path.join(sdir(x), "..\\Build\\Debug log.txt"))

bl = build_log

def build_log_open(x):
    blx = build_log(x)
    print(x, blx)
    if os.path.exists(blx): npo(blx)
    else: sys.exit("No build log for", x, "at", blx)

blo = bl_o = build_log_open

def hdr(x, y, base=False, github=False):
    if proj_exp(y, False) and x in i7hfx and not proj_exp(x, False): (x, y) = (y, x) # if x is a header and not a project, flip x and y
    x = main_abb(x, use_given = True)
    if y in ( 'ni', 'main', 'story' ):
        return(main_src(x))
    base_file_name = '{:s} {:s}.i7x'.format(lpro(x, nonblank=True).title(), i7hfx[y].title() if y in i7hfx else y.title())
    temp = '{:s}\{:s}'.format(extdir, base_file_name)
    if base:
        return os.path.basename(temp)
    if github:
        return '{:s}\{:s}\{:s}'.format(gh_dir, dict_val_or_similar(dict_val_or_similar(x, i7gx), i7x), base_file_name)
    return temp

headerfile = header = hdrfile = hdr_file = hfile = hdr

def invis_file(x, warning=False):
    try_1 = "c:/writing/scripts/invis/{:s}.txt".format(i7xr[x] if x in i7xr.keys() else x)
    if os.path.exists(try_1): return try_1
    if warning: print("WARNING no invisiclues file for", x)
    return ""

def notes_file(x, suffix=''):
    notes_local = "notes{}.txt".format('-' + suffix if suffix else '')
    if x in i7com:
        combo_try = "c:/Users/Andrew/Documents/github/configs/notes/notes-{}.txt".format(main_abb(x))
        if os.path.exists(combo_try):
            return combo_try
    return os.path.join(sdir(x), notes_local)

def walkthrough_file(x, extra_string = ""):
    if extra_string == 'base' or extra_string == 'wbase':
        file_short = "wbase.txt"
    else:
        file_short = "walkthrough" + ( '-' + extra_string if extra_string else '') + ".txt"
    return os.path.join(sdir(x), file_short)

wthru = walkthrough_file

def mistake_file(x):
    return '{:s}\{:s} Mistakes.i7x'.format(extdir, lpro(x, True).title())

mifi = mistake_file

def table_file(x):
    return '{:s}\{:s} Tables.i7x'.format(extdir, lpro(x, True).title())

tafi = table_file

def test_file(x):
    return '{:s}\{:s} Tests.i7x'.format(extdir, lpro(x, True).title())

tefi = test_file

def triz_map_of(x):
    x2 = proj_exp(x)
    base_name = dictish(x2, i7triz)
    if not base_name:
        base_name = dictish(x2, i7x)
    return os.path.join(triz_dir, "{:s}.trizbort".format(base_name))

triz = triz_file = triz_map = triz_map_of

def hf_exp(x, return_nonblank = True):
    xl = x.lower()
    if xl in i7hfx.keys(): return i7hfx[xl].title()
    if xl in i7hfx.values(): return xl.title()
    else: return xl.title()

th_exp = hf_exp

def proj_exp(x, return_nonblank = True, to_github = False):
    if '/' in x:
        ary = x.split('/')
        if ary[0] in i7com and ary[1] in i7com[ary[0]].split(','):
            x = ary[1]
    if to_github:
        temp = x
        if temp in i7xr.keys(): temp = i7xr[temp]
        if temp in i7gx.keys(): return i7gx[temp]
    if x in i7xr.keys(): return x
    elif x in i7x.keys(): return i7x[x]
    if x.lower() in i7com: return x
    return (x if return_nonblank else '')

pex = proj_exp

def hfi_exp(x, return_nonblank = True):
    if x in i7nonhdr.keys(): return i7nonhdr[x]
    if x in i7nonhdr.values(): return x
    if return_nonblank: return x
    return ""

def lpro(x, nonblank = False, spaces = True):
    retval = proj_exp(x, nonblank)
    if spaces: retval = re.sub("-", " ", retval)
    return retval

def has_ni(x):
    if os.path.exists(os.path.join(x, "story.ni")): return True
    my_proj = proj2dir(dir2proj(x))
    if os.path.exists(os.path.join(my_proj, "story.ni")): return True
    return False

def dir2proj(x = os.getcwd(), to_abbrev = False, empty_if_unmatched = True, return_first_subfind = False, default_if_unmatched = False):
    x0 = x.lower()
    x2 = ""
    ary = pathlib.PurePath(x).parts
    if " materials" in x0:
        for a in ary:
            if 'materials' in a.lower():
                x2 = re.sub(" Materials", "", a, re.IGNORECASE)
        if not x2:
            sys.stderr.write("WARNING: {} should've mapped to a project but didn't.".format(x))
    elif 'github' in ary and ary.index('github') < len(ary) - 1:
        ghi = ary.index('github') + 1
        long_match = '/'.join(ary[ghi:])
        x2 = ary[ghi]
        for x in range(ary.index('github') + 2, len(ary)):
            if os.path.exists(os.path.join(pathlib.Path(*ary[:x]), "story.ni")):
                x2 = ary[x-1]
                if return_first_subfind:
                    break
        for x in i7gxr:
            if long_match.startswith(x):
                x2 = x
                break
    elif os.path.exists(os.path.join(x0, "story.ni")) or ".inform" in x0: # this works whether in the github or inform directory
        for a in ary:
            if ".inform" in a:
                x2 = re.sub("\.inform", "", a)
            elif a.lower() in i7xr:
                x2 = a.lower()
            elif a.lower() in i7x:
                x2 = i7x[a.lower()]
        if not x2 and not x:
            sys.stderr.write("WARNING: {} should've mapped to a project but didn't.\n".format(x))
    x2 = x2.lower()
    if x2 in i7xr: # in some case, a double-reversal might not work e.g. compound -> pc -> the-problems-compound
        x3 = i7xr[x2]
        if to_abbrev:
            return x3
        if x3 in i7x:
            return i7x[x3]
    if x2 in i7gxr: # this is for irregularly named projects that lead to story.ni, e.g. stale-tales-slate/roiling to roiling
        x3 = i7gxr[x2]
        if to_abbrev:
            return x3
        if x3 in i7x:
            return i7x[x3]
    if default_if_unmatched and x2 not in i7xr:
        return curdef
    if empty_if_unmatched and x2 not in i7xr:
        return ""
    return x2

def inform_short_name(my_file, acknowledge_dailies = True):
    retval = os.path.basename(my_file)
    if retval.startswith('reg-') or retval.startswith('rbr-'):
        return retval
    if 'i7x' in retval:
        return retval.replace('.i7x', '')
    if retval in i7gsn:
        temp_proj = dir2proj(my_file).replace('-', ' ').title()
        if temp_proj:
            return "{} {}".format(temp_proj, i7gsn[retval])
        else:
            return "{}".format(i7gsn[retval])
    if acknowledge_dailies and mt.is_daily(my_file):
        if 'keep' in my_file:
            return "(keep) {}".format(retval)
        elif 'drive' in my_file:
            return "(drive) {}".format(retval)
        elif 'daily' in my_file:
            return "({}daily) {}".format('current ' if 'to-proc' not in my_file else '', retval)
        else:
            return "(YYYYMMDD notes) {}".format(retval)
    if retval.startswith("notes-"):
        base = re.sub("\..*", "", retval[6:])
        return "{} notes".format(long_name(base, strip_dashes = True).title())
    return '* ({})'.format(retval)

def proj2root(x = dir2proj()):
    return "c:\\games\\inform\\{:s}.inform".format(proj_exp(x))

def proj2dir(x = dir2proj(), my_subdir = "", to_github = False, materials = False, bail_if_nothing = False, default_subdir = True):
    if default_subdir and not my_subdir:
        if materials:
            my_subdir = "Release"
        else:
            my_subdir = "Source"
    if to_github:
        if x and os.path.isdir(os.path.join(gh_dir, x)):
            return os.path.normpath(os.path.join(gh_dir, x))
        temp = main_abb(x)
        if not temp:
            temp = x
        if temp in i7gx:
            temp = i7gx[temp]
        elif temp in i7x:
            temp = i7x[temp]
        elif bail_if_nothing:
            sys.exit("Didn't find github repo to dir2proj for {}. Bailing.".format(x))
        else:
            return ''
        return os.path.join(gh_dir, temp)
    return "c:\\games\\inform\\{}{}{}".format(proj_exp(x), " Materials" if materials else ".inform", ("\\" + my_subdir) if my_subdir else "")

sdir = p2d = proj2dir

def ghtest(x = dir2proj()):
    return os.path.normpath(os.path.join(proj2dir(x, to_github = True), 'testing'))

def ghutils(x = dir2proj()):
    return os.path.normpath(os.path.join(proj2dir(x, to_github = True), 'utils'))

def proj2mat(x = dir2proj()):
    return proj2dir(x, my_subdir = "", materials = True)

matdir = proj2mat

def proj2matr(x = dir2proj()):
    return proj2dir(x, my_subdir = "Release", materials = True)

matrel = proj2matr

def cover_art(x, small = False, bail = True):
    stem = "Small Cover" if small else "Cover"
    for q in [ 'png', 'jpg' ]:
        temp = os.path.join(proj2matr(x), "{}.{}".format(stem, q))
        if os.path.exists(temp):
            return temp
    sys.stderr.write("Could not find cover art for {}.".format(x))
    if bail:
        exit()
    return ""

def small_cover_art(x):
    return cover_art(x, small = True)

def go_proj(x, my_subdir = "source", to_github = False, materials = False):
    if materials and my_subdir == "source":
        my_subdir = ""
    os.chdir(proj2dir(x, my_subdir, to_github, materials))
    return

go_p = proj_dir = to_proj = go_proj

sproj = d2p = dir2proj

npo = mt.npo

def combo_of(my_proj):
    proj_alt = i7x[my_proj] if my_proj in i7x else ""
    for x in i7com:
        for y in i7com[x].split(','):
            if y == my_proj or y == proj_alt: return x
    #if x in i7x: return combo_of[i7x[x]]
    return my_proj

def rbr(my_proj = dir2proj(), need_one = True, file_type = "thru"):
    if not my_proj: my_proj = dir2proj()
    if my_proj in i7xr: my_proj = i7xr[my_proj]
    elif my_proj not in i7x: return ""
    base_dir = proj2dir(my_proj)
    first_try = os.path.join(base_dir, "rbr-{}-{}.txt".format(my_proj, file_type))
    if os.path.exists(first_try): return first_try
    for x in i7x:
        if i7x[x] == i7x[my_proj]:
            next_try = os.path.join(base_dir, "rbr-{}-{}.txt".format(x, file_type))
            if os.path.exists(next_try): return next_try
    sys.exit("WARNING tried to get one file from rbr for {} and failed".format(my_proj))

def read_latest_project():
    global latest_project_abbr
    global latest_project_long
    with open(i7_temp_config) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith('#'):
                continue
            if line.startswith(';'):
                break
            (prefix, data) = mt.cfg_data_split(line)
            if prefix == 'current':
                latest_project_abbr = main_abbr(data)
                latest_project_long = long_name(data)
            else:
                print("WARNING i7d.txt bad temp-config line {} = {}".format(line_count, line.strip()))
    return (latest_project_abbr, latest_project_long)

read_latest_proj = read_latest_project

def write_latest_project(proj_to_write, give_success_feedback = True):
    file_write_string = ''
    any_diff = False
    any_current = False
    abbr_to_write = main_abbr(proj_to_write)
    with open(i7_temp_config) as file:
        for (line_count, line) in enumerate (file, 1):
            (prefix, data) = mt.cfg_data_split(line)
            if prefix == 'current':
                any_current = True
                next_string = "current={}\n".format(abbr_to_write)
                if next_string.lower() != line.lower():
                    any_diff = True
                file_write_string += next_string
            else:
                file_write_string += line
    if not any_current:
        print("Not writing latest project file as I found no current= line.")
    elif not any_diff:
        print("Not writing latest project file as default project wasn't changed: {} is already the default project.".format(proj_to_write))
        return
    try:
        f = open(i7_temp_config, "w")
        f.write(file_write_string)
        f.close()
    except:
        print("Tried to write over the temp-config file, but it didn't work.")
        return
    if give_success_feedback:
        print("Successfully changed latest-project to", abbr_to_write)

write_latest_proj = write_latest_project

def see_uniq_and_vers(args):
    if args[0] == '-': args = args[1:]
    print("Testing verxions/release #s/etc")
    verbose = False
    release_test = False
    if 'v' in args: verbose = True
    if 'r' in args: release_test = True
    i7rev = defaultdict(list)
    for x in i7x.keys():
        i7rev[i7x[x]].append(x)
    if release_test:
        for y in sorted(i7rev.keys()):
            if y not in i7rn.keys(): print(y, "needs a release number or file name")
    for y in sorted(i7rev.keys()):
        if len(i7rev[y]) == 1:
            # print(y, "is unique")
            if y in i7xr.keys():
                print(y, "doesn't need to be in i7xr. It is uniquely defined from", i7xr[y] + '.')
            else:
                if verbose: print("Defining", y, "reverse to", i7rev[y][0] + '.')
                i7xr[y] = i7rev[y][0]
        else:
            # print(y, "is mapped to", len(i7rev[y]), "different values:", i7rev[y])
            if y not in i7xr.keys():
                print(y, "should be in i7xr, with", len(i7rev[y]), "different values.")

def revprojx(a):
    if a in i7xr.keys(): return i7xr[a]
    a = re.sub("\.inform.*", "", a)
    a = re.sub(".*[\\\/]", "", a)
    if a in i7xr.keys(): return i7xr[a]
    return a

def revproj(a):
    return_val = ""
    if a in i7xr.keys(): return i7xr[a]
    for b in i7x.keys():
        if i7x[b] == a:
            if return_val:
                print("\n\n****FIX IMMEDIATELY IN I7.PY (I7X/I7XR):", return_val, "and", b, "both map to", a)
                exit()
            return_val = b
    return return_val

def i7fa(p):
    if p in i7x: p = i7x[p]
    retary = i7f[p]
    for q in set(i7nonhdr.values()):
        if q == 'story.ni': continue
        temp = os.path.join(main_src(p), q)
        if os.path.exists(temp): retary.append(temp)
    return retary

def ext2blorb(game_ext, return_error = True, return_blank = False):
    if game_ext == 'ulx':
        return 'gblorb'
    if game_ext == 'z8' or game_ext == 'z5':
        return 'zblorb'
    if return_error:
        return 'err'
    if return_blank:
        return ''
    sys.exit("Could not convert extension {} to blorb. Bailing. Set return_error or return_blank to skip this.".format(game_ext))

def ext2blorb(y):
    if y.startswith('z'):
        return 'zblorb'
    return 'gblorb'

def bin_ext(x, to_blorb = False):
    if to_blorb:
        return ext2blorb(x)
    return x

def bin_file(x, my_ext, file_type = RELEASE, to_blorb = False):
    if file_type != DEBUG:
        if inish(x, i7binname):
            my_file = i7binname[x]
        else:
            my_file = proj_exp(x)
    else:
        my_file = "output"
    my_file = my_file.replace('-', ' ')
    my_dir = "c:/games/inform/{}{}/{}".format(proj_exp(x), ' Materials' if file_type == RELEASE else '.inform', 'Release' if file_type == RELEASE else 'Build')
    if file_type == BETA:
        my_file = "beta-" + my_file
    if not os.path.exists(my_dir):
        print("WARNING tried to find materials/release directory {} from {} and failed.".format(my_dir, x))
    x0 = main_abb(x)
    my_file += "." + bin_ext(my_ext, to_blorb)
    return os.path.normpath(os.path.join(my_dir, my_file))

def all_proj_fi(x, bail = True):
    xp = i7xr[x] if x in i7xr.keys() else x
    if xp not in i7com.keys():
        if bail: raise("No full project named {:s}".format(x))
        return []
    ary = []
    for q in i7com[xp].keys(): ary += i7f[q]
    return ary

apf = all_proj_fi

def apostrophe_check_string(my_string, print_results = False, my_file = '<UNDEFINED>', line_num = -1, require_quoted = True):
    if require_quoted and '"' not in my_string: return 0
    ml = my_string.strip()
    lefts = re.findall(r"[^a-zA-Z!,.?\]]'", ml)
    rights = re.findall(r"'[^a-zA-Z!,.?]", ml) # we can have the start of a [one of/or] after quotes, but ]' is a bit awkward. Exceptions have [apostrophe ok].
    ll = len(lefts)
    rl = len(rights)
    if ll != rl and "[apostrophe ok]" not in my_string:
        if print_results:
            print("potential bad apostrophes (ignore with [apostrophe ok]) {} to {} {} line {} >>> {}".format(abs(ll-rl), "left" if ll > rl else "right", os.path.basename(my_file), line_num if line_num > -1 else "<NO LINE>", ml))
    return abs(ll - rl)

def is_vardef_line(my_line):
    mll = my_line.lower().strip()
    mll = re.sub(" +", " ", mll)
    if "is a list of" in my_line and "variable" in line: return True
    if re.search("is a (number|truth state|thing|room) that varies", my_line): return True
    return False

def search_defs(my_file_array, print_defs = False, print_success = True):
    defs_found = 0
    files_passed = 0
    files_failed = 0
    if type(my_file_array) == str:
        my_file_array = [ my_file_array ]
    for my_file in my_file_array:
        mf = os.path.basename(my_file).lower()
        if 'definitions' in mf: continue
        this_failed = False
        with open(my_file) as file:
            for (line_count, line) in enumerate(file, 1):
                if is_vardef_line(line):
                    defs_found += 1
                    this_failed = True
                    if print_defs:
                        print("DEF {} at {} line {}: {}".format(defs_found, mf, line_count, line.rstrip()))
        files_passed += (defs_found == 0)
        files_failed += (defs_found != 0)
        if print_defs and defs_found == 0:
            print("No definitions in {}.{}".format(my_file, ' Success!' if print_success else ''))
    if len(my_file_array) > 1:
        print("Files passed: {} Files failed: {}.".format(files_passed, files_failed))
    return defs_found

def apostrophe_check_line(my_line, print_results = False, my_file = '<UNDEFINED>', line_num = -1):
    retval = 0
    for x in re.split("\t+", my_line.strip()):
        retval += apostrophe_check_string(x, print_results, my_file, line_num)
    return retval

# here is where we sort out stuff like abbreviations and header files

with open(i7_cfg_file) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith(';'): break
        if line.startswith('#'): continue
        ll = line.lower().strip()
        lln = re.sub("^.*?:", "", ll)
        if ':' not in ll and '=' not in ll: print("WARNING line", line_count, "in i7p.txt needs = or :.")
        lla = lln.split("=")
        lli = re.sub(":.*", "", ll)
        if ll.startswith("headname:"):
            for x in lla[1].split(","): i7hfx[x] = lla[0]
            continue
        if ll.startswith("ignore:"):
            i7ignore.extend(lln.split(','))
            continue
        if ll.startswith("nonhdr:"):
            for x in lla[1].split(","): i7nonhdr[x] = lla[0]
            continue
        if ll.startswith("bitbucket:"):
            i7bb = re.sub(".*:", "", ll).split(",")
            continue
        if ll.startswith("github:"):
            i7gh = re.sub(".*:", "", ll).split(",")
            continue
        if ll.startswith("curdef:"):
            curdef = lln
            continue
        if ll.startswith("release:"):
            i7rn[lla[0]] = lla[1]
            continue
        if ll.startswith("trizbort:"):
            i7triz[lla[0]] = lla[1]
            continue
        if ll.startswith("trizmaps:"):
            llproj = lln.split(":")
            llpre = llproj[1].split(",")
            for llp in llpre:
                temp = llp.split("=")
                if temp[1].startswith("tm"):
                    temp[1] = os.path.join(triz_dir, temp[1][3:])
                else:
                    temp[1] = os.path.join(proj2dir(llproj[0]), temp[1])
                for q in temp[0].split("/"):
                    i7trizmaps[llproj[0]][q]=temp[1]
            continue
        if ll.startswith("combo:"):
            i7com[lla[0]] = lla[1]
            subproj = lla[1].split(",")
            for x in range(0, len(subproj)):
                i7comord[lla[0]][subproj[x]] = x + 1
                i7comr[subproj[x]] = lla[0]
            continue
        if ll.startswith("ghproj:"):
            i7gx[lla[1]] = lla[0]
            i7gxr[lla[0]] = lla[1]
            continue
        if ll.startswith("genshort:"):
            i7gsn[lla[0]] = lla[1]
            continue
        if ll.startswith("binext:"):
            for temp in lla[0].split(","):
                i7gbx[temp] = lla[1].split(",")
            continue
        if ll.startswith("auxfile:"):
            for temp in lla[0].split(","):
                i7aux[temp] = lla[1].split(",")
            continue
        if ll.startswith("compile-"):
            this_bin = i7gbx[re.sub(".*-", "", lli)]
            for x in lla[0].split(","):
                if not main_abb(x):
                    print("Line {} has faulty project/abbreviation {} for compile binary extensions.".format(line_count, x))
                if main_abb(x) in i7pbx:
                    print("Redefinition of {}/{} project binaries at line {}.".format(x, main_abb(x), line_count))
                i7pbx[main_abb(x)] = this_bin
            continue
        if ll.startswith("binname:"):
            i7binname[lla[0]] = re.sub(".*=", "", line.strip()) # I want to keep case here
            continue
        combos = False
        l0 = line.lower().strip().split("=")
        l0p = re.sub(".*:", "", l0[0])
        l1 = l0[1].split(",")
        if l0[0].startswith("headers:"):
            if l0p in i7com:
                i7f[l0p] = []
                i7fg[l0p] = []
            else:
                i7f[l0p] = [ src(l0p) ]
                i7fg[l0p] = [ gh_src(l0p) ]
            for q in l1:
                i7f[l0p].append(hdr(l0p, q))
                i7fg[l0p].append(hdr(l0p, q, github=True))
            continue
        if ":" in ll:
            print("WARNING: for I7 python, line {:d} has an unrecognized colon: {:s}".format(line_count, ll))
            continue
        if "=" not in line:
            print("WARNING line", line.strip(), "needs ; # or =")
            continue
        for my_l in l1:
            if combos: i7com[my_l] = l1
            else:
                i7x[my_l] = l0[0]
                i7xr[l0[0]] = l1[0]
    for q in i7x.keys():
        if i7x[q] in i7com.keys():
            i7com[q] = i7com[i7x[q]]

def get_trizbort_rooms(file_name, keep_punctuation = True, ignore_regions = [], get_all_slash = False):
    triz = defaultdict(str)
    try:
        e = ET.parse(file_name)
    except:
        print("Couldn't find", file_name)
        exit()
    root = e.getroot()
    for elem in e.iter('room'):
        if elem.get('name'):
            if elem.get('region') and elem.get('region').lower() in ignore_regions: continue
            x = str(elem.get('name')).lower()
            x = re.sub(" *\(.*\)", "", x) # get rid of parenthetical/alternate name
            if not keep_punctuation:
                x = mt.strip_punctuation(x, zap_bounding_apostrophe = True)
            stuf_ary = re.split(" */ *", x) # optional for if a room name changes
            if get_all_slash:
                for q in stuf_ary:
                    triz[q] = str(elem.get('region')).lower()
            else:
                triz[stuf_ary[0]] = str(elem.get('region')).lower()
        # print (x,triz[x])
        # triz[atype.get('name')] = 1;
    return triz

triz_rooms = get_triz_rooms = trizbort_rooms = get_trizbort_rooms

def _valid_i7m_arg(x):
    if x[0] == '-': x = x[1:];
    if '?' not in x: return False
    x = re.sub("\?", "", x)
    return re.search("^[rv]*$", x)

def rmbrax(my_str, spaces_too = True, end_only = False, replace_string = "", skip_formatting = True):
    if skip_formatting:
        my_str = re.sub("\[(b|i|r)\]", "", my_str)
    regex_str = "\[[^\]]*\]"
    if spaces_too: regex_str = " *" + regex_str + " *"
    if end_only: regex_str += "$"
    my_str = re.sub(" *\[[^\]]*\] *", replace_string, my_str)
    return my_str

def get_defined_region(l): # we assume that a region is defined in the first sentence.
    l = re.sub("\..*", "", l)
    if l.startswith("there is"):
        return re.sub("there is a region called ", "", l, 0, re.IGNORECASE)
    return re.sub(" is a region.*", "", l, 0, re.IGNORECASE)

def escape_brackets(my_string):
    temp = my_string.replace("[", "\[")
    temp = temp.replace("]", "\]")
    return temp

def all_branches(conditional_string):
    if "[" not in conditional_string:
        yield conditional_string
        return
    ary = re.split("\[[^\]]*\]", conditional_string)[1:-1]
    if len(ary) == 1 and (conditional_string.startswith("[if") or conditional_string.startswith("[unless")):
        ary.append("<BLANK: possibly add to beginning of line: !{}>".format(ary[0]))
    for y in ary:
        yield y
    return

def first_fragment_of(string_gen, start_match, end_match):
    ary = []
    find_all_string = "{}.*?{}".format(escape_brackets(start_match), escape_brackets(end_match))
    if "(" in find_all_string:
        find_all_string = "({})".format(find_all_string)
    for st in string_gen:
        if not re.findall(find_all_string, st):
            yield(st)
            continue
        x = re.findall(find_all_string, st)
        if type(x[0]) == tuple:
            x = list(x[0])
        lab = list(all_branches(x[0]))
        if not len(lab):
            sys.exit("Oops, bad branching for {} {} {}".format(string_gen, start_match, end_match))
        for y in list(all_branches(x[0])):
            yield(st.replace(x[0], str(y)))

def all_possible_fragments(text_string, start_match, end_match, bail = True):
    array_to_expand = [text_string]
    start_match_adj = escape_brackets(start_match)
    end_match_adj = escape_brackets(start_match)
    if start_match_adj and not end_match_adj:
        print("BAD MATCHING")
        print(text_string)
        print(start_match_adj)
        print(end_match_adj)
        if bail: sys.exit()
    while re.findall(start_match_adj, array_to_expand[0]):
        last_len = len(array_to_expand)
        array_gen = first_fragment_of(array_to_expand, start_match, end_match)
        array_to_expand = list(array_gen)
        if last_len == len(array_to_expand):
            break
    return array_to_expand

def all_if_fragments(text_string):
    if ("[end if][end if]") in text_string:
        print("WARNING recursive endifs may make trouble:")
        print("    ", text_string)
    return all_possible_fragments(text_string, "[(if|unless) ", "[end if]")

def all_oneof_fragments(text_string):
    return all_possible_fragments(text_string, "[one of]", "[(stopping|in random order|at random)]")

def if_oneof_crude_convert(text_string):
    text_string = text_string.replace("[']", "'")
    temp_array = all_if_fragments(text_string)
    return_array = []
    for x in temp_array:
        return_array.extend(all_oneof_fragments(x))
    return return_array

def header_file_from_line(my_line):
    temp = my_line.replace('.', '').split()
    my_dir = os.path.join(ext_root, "{} {}".format(temp[-2], temp[-1]))
    my_file = ' '.join(temp[1:-3]) + ".i7x"
    return os.path.join(my_dir, my_file)

def flat_header_list(my_file):
    my_list = []
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("include") and " by " in line:
                temp = header_file_from_line(line)
                if temp not in my_list:
                    my_list.append(temp)
    return my_list

def recursive_header_list(my_file, my_current_list = []):
    temp = flat_header_list(my_file)
    for x in temp:
        x = os.path.realpath(x)
        if x in my_current_list:
            continue
        my_current_list.append(x)
        my_current_list = recursive_header_list(x, my_current_list)
    return my_current_list

def open_table(this_proj = dir2proj(), table_name = '', special_text = '', special_column = -1, bail = True):
    if not this_proj:
        print("Tried to open table {} in {} but failed.".format(table_name, this_proj))
        return
    full_table = "table of " + table_name
    this_proj = long_name(this_proj)
    table_start_line = table_end_line = table_detail_line = 0
    got_one = False
    for my_file in i7f[this_proj]:
        fb = os.path.basename(my_file)
        in_my_table = False
        table_start_line = 0
        with open(my_file) as file:
            for (line_count, line) in enumerate (file, 1):
                if line.startswith(full_table):
                    if "\t" in line:
                        print("Table name found with tabs at {} line {}.".format(fb, line_count))
                        continue
                    table_start_line = line_count
                    in_my_table = True
                elif not line.strip():
                    if in_my_table:
                        table_end_line = line_count
                    in_my_table = False
                elif in_my_table and special_text:
                    if special_column == -1:
                        if special_text in line.lower():
                            table_detail_line = line_count
                            break
                    else:
                        ary = line.split("\t")
                        if special_text in ary[special_column].lower():
                            table_detail_line = line_count
                            break
        if table_start_line > 0 and table_end_line == 0:
            table_end_line = line_count
        if table_detail_line > 0:
            mt.npo(my_file, table_detail_line)
            got_one = True
        elif special_text and table_start_line > 0 and table_end_line > 0:
            print("Opening the middle of the table since I couldn't find", special_text)
            mt.npo(my_file, (table_start_line + table_end_line) / 2)
            got_one = True
        elif table_start_line > 0:
            mt.npo(my_file, table_start_line)
            got_one = True
    if not got_one:
        print("Unable to find {} in any {} files.".format(full_table, this_proj))

#put unit tests for new functions here, then run i7.py
#move them where needed for future reference

if os.path.basename(main.__file__) == "i7.py":
    if len(sys.argv) > 1:
        if sys.argv[1] == '?': i7_usage()
        if sys.argv[1] == 'e': oc()
        if _valid_i7m_arg(sys.argv[1]): see_uniq_and_vers(sys.argv[1])
        else: print("Not a valid argument for the i7 module. ?, e, -[rv].")
        exit()
    print("i7.py is a header file. It should not be run on its own.")
    print("Try running something else with the line import i7, instead, or ? to run a test.")
    # see_uniq_and_vers()
    exit()
