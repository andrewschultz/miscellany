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
# todo: erase i7c and see where i7c pops up in other Python files in the whole tree.
#

import xml.etree.ElementTree as ET
from collections import defaultdict
import mytools as mt
import sys
import re
import os
import glob
from filecmp import cmp
from shutil import copy
import __main__ as main

auth = "Andrew Schultz"
extdir = r'c:\Program Files (x86)\Inform 7\Inform7\Extensions\{:s}'.format(auth)
nice = nz = nicez = os.path.join(extdir, "Trivial Niceties Z-Only.i7x")
niceg = ng = os.path.join(extdir, "Trivial Niceties.i7x")
tmp_hdr = temp_hdr = tmp_header = temp_header = os.path.join(extdir, "temp.i7x")
np = mt.np
f_dic = "c:/writing/dict/brit-1word.txt"
f_f = "c:/writing/dict/firsts.txt"
f_l = "c:/writing/dict/lasts.txt"
prt = "c:/games/inform/prt"
prt_temp = os.path.join(prt, "temp")
i7_cfg_file = "c:/writing/scripts/i7p.txt"
triz_dir = "c:\\games\\inform\\triz\\mine"
gh_dir = "c:\\users\\andrew\\documents\\GitHub"
beta_dir = "c:/games/inform/beta Materials/Release"

# these are default values for binaries--debug is assumed to be most important
# since it is the one I'll be using the most.
# beta is used for automation.
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

def main_abb(x):
    if x in i7xr:
        return i7xr[x]
    if x not in i7x: return ""
    if i7x[x] not in i7xr:
        print("    **** I7.PY WARNING {}/{} does not have reverse abbreviation.".format(x, i7x[x]))
        return ""
    return i7xr[i7x[x]]

def dict_val_or_similar(my_key, my_dict):
    if my_key in my_dict:
        return my_dict[my_key]
    if my_key in i7xr and i7xr[my_key] in my_dict:
        return my_dict[i7xr[my_key]]
    if my_key in i7x and i7x[my_key] in my_dict:
        return my_dict[i7x[my_key]]
    if main_abb(my_key) in my_dict:
        return my_dict[main_abb(my_key)]
    return False

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

def topics_to_array(x, div_char = "/"):
    x = re.sub("^\"*", "", x)
    my_topic_array = zap_end_brax(x).split('"')[0::2] # every other quoted thing, minus comments at the end
    overall_array = []
    for myt in my_topic_array:
        base_array = ['']
        tary = myt.split(" ")
        for g in tary:
            temp_stuff = g.split(div_char)
            new_base_array = []
            for t in temp_stuff:
                for x in base_array:
                    new_base_array.append((x + " " if x else "") + t)
            base_array = list(new_base_array)
        overall_array.extend(base_array)
    return overall_array

topx2ary = topics_to_array

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
plur = mt.wm
wm = mt.wm

def remove_quotes(x):
    temp = re.sub("\"", "", x)
    temp = re.sub("\".*", "", x)
    return temp

rq = remove_quotes

def gh_src(x, give_source = True):
    temp = proj_exp(x, to_github = True)
    retval = os.path.join(gh_dir, temp)
    if give_source: retval = os.path.join(retval, "story.ni")
    return os.path.normpath(retval)

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

uuid = uuid_file = uid_file

def auto_file(x):
    return os.path.normpath(os.path.join(proj2root(x), "auto.inf"))

def main_src(x):
    return os.path.normpath(os.path.join(sdir(x), "story.ni"))

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

def hdr(x, y, base=False):
    if proj_exp(y, False) and x in i7hfx and not proj_exp(x, False): (x, y) = (y, x) # if x is a header and not a project, flip x and y
    temp = '{:s}\{:s} {:s}.i7x'.format(extdir, lpro(x, True).title(), i7hfx[y].title() if y in i7hfx else y.title())
    if base:
        return os.path.basename(temp)
    return temp

hdrfile = hfile = hdr

def invis_file(x, warning=False):
    try_1 = "c:/writing/scripts/invis/{:s}.txt".format(i7xr[x] if x in i7xr.keys() else x)
    if os.path.exists(try_1): return try_1
    if warning: print("WARNING no invisiclues file for", x)
    return ""

def notes_file(x):
    return sdir(x) + "/" + "notes.txt"

def walkthrough_file(x, extra_string = ""):
    return sdir(x) + "/" + "walkthrough" + ( '-' + extra_string if extra_string else '') + ".txt"

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

def triz(x):
    x2 = proj_exp(x)
    return os.path.join(triz_dir, "{:s}.trizbort".format(i7triz[x2] if x2 in i7triz.keys() else x2))

triz_file = triz

def hf_exp(x, return_nonblank = True):
    xl = x.lower()
    if xl in i7hfx.keys(): return i7hfx[xl].title()
    if xl in i7hfx.values(): return xl.title()
    else: return xl.title()

th_exp = hf_exp

def proj_exp(x, return_nonblank = True, to_github = False):
    if to_github:
        temp = x
        if temp in i7xr.keys(): temp = i7xr[temp]
        if temp in i7gx.keys(): return i7gx[temp]
    if x in i7xr.keys(): return x
    elif x in i7x.keys(): return i7x[x]
    if x.lower() == 'sts': return x
    return (x if return_nonblank else '')

pex = proj_exp

def hfi_exp(x, return_nonblank = True):
    if x in i7nonhdr.keys(): return i7nonhdr[x]
    if x in i7nonhdr.values(): return x
    if return_nonblank: return x
    return ""

def lpro(x, spaces=False):
    retval = proj_exp(x, False)
    if spaces: retval = re.sub("-", " ", retval)
    return retval

def has_ni(x):
    if os.path.exists(os.path.join(x, "story.ni")): return True
    my_proj = proj2dir(i7.dir2proj(x))
    if os.path.exists(os.path.join(my_proj, "story.ni")): return True
    return False

def proj2root(x):
    return "c:\\games\\inform\\{:s}.inform".format(proj_exp(x))

def proj2dir(x):
    return "c:\\games\\inform\\{:s}.inform\\source".format(proj_exp(x))

sdir = p2d = proj2dir

def proj2mat(x):
    return "c:\\games\\inform\\{:s} Materials".format(proj_exp(x))

matdir = proj2mat

def proj2matr(x):
    return "c:\\games\\inform\\{:s} Materials\\Release".format(proj_exp(x))

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

def go_proj(x):
    os.chdir(proj2dir(x))
    return

go_p = proj_dir = to_proj = go_proj

def dir2proj(x = os.getcwd(), to_abbrev = False):
    x0 = x.lower()
    x2 = ""
    if os.path.exists(x0 + "\\story.ni") or ".inform" in x: # this works whether in the github or inform directory
        x2 = re.sub("\.inform.*", "", x0)
        x2 = re.sub(".*[\\\/]", "", x2)
    elif " materials" in x0:
        x2 = re.sub(" materials.*", "", x0)
        x2 = re.sub(".*[\\\/]", "", x2)
    elif re.search("documents.github..", x0):
        x2 = re.sub(".*documents.github.", "", x0, 0, re.IGNORECASE)
        x2 = re.sub("[\\\/].*", "", x2)
        if not re.search("[a-z]", x2): return ""
    if "\\" in x2 or "/" in x2 or not x2: return ""
    if to_abbrev and x2 in i7xr: return i7xr[x2]
    return x2

sproj = d2p = dir2proj

npo = mt.npo

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

def bin_ext(x, file_type = BETA, to_blorb = False):
    if not inish(x, i7pbx):
        out_type = 'ulx'
    else:
        out_type = dictish(x, i7pbx)[file_type]
    if to_blorb:
        out_type = ext2blorb(out_type)
    return out_type

def bin_file(x, file_type = BETA, to_blorb = False):
    if inish(x, i7binname):
        my_file = i7binname[x]
    else:
        my_file = proj_exp(x).replace('-', ' ')
    my_dir = beta_dir if file_type == BETA else "c:/games/inform/{} materials/Release".format(proj_exp(x))
    if file_type == BETA:
        my_file = "beta-" + my_file
    if not os.path.exists(my_dir):
        print("WARNING tried to find materials/release directory {} from {} and failed.".format(my_dir, x))
    x0 = main_abb(x)
    my_ext = bin_ext(x0, file_type, to_blorb)
    my_file += "." + my_ext
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

def apostrophe_check_string(my_string, print_results = False, my_file = '<UNDEFINED>', line_num = -1):
    ml = my_string.strip()
    lefts = re.findall(r"[^a-zA-Z!,.?\]]'", ml)
    rights = re.findall(r"'[^a-zA-Z!,.?]", ml) # we can have the start of a [one of/or] after quotes, but ]' is a bit awkward. Exceptions have [apostrophe ok].
    ll = len(lefts)
    rl = len(rights)
    if ll != rl and "[apostrophe ok]" not in my_string:
        if print_results:
            print("potential bad apostrophes {} to {} {} line {} >>> {}".format(abs(ll-rl), "left" if ll > rl else "right", os.path.basename(my_file), line_num if line_num > -1 else "<NO LINE>", ml))
    return abs(ll - rl)

def apostrophe_check_line(my_line, print_results = False, my_file = '<UNDEFINED>', line_num = -1):
    retval = 0
    for x in re.split("\t+", my_line.strip()):
        retval += apostrophe_check_string(x, print_results, my_file, line_num)
    return retval

i7c = {
  "sts": ["roiling", "shuffling"],
  "ops": ["threediopolis", "fourdiopolis"],
  "as": ["slicker-city", "compound", "buck-the-past", "seeker-status" ]
}

#
# some of these may have underscores due to how I named the release files
# e.g. shuffling -> shuffling_around
#
# I could create i7full but that would be arduous

# i7 defined arrays for both perl/python files
# read from i7p.txt/i7_cfg_file

i7gx = {} # github project renaming e.g. compound -> the_problems_compound. Most of the time this won't matter--GH = what's on my computer
i7x = {} # mapping abbreviation to main project e.g. ai = ailihphilia
i7xr = {} # mapping main project to unique/main abbreviation e.g. buck-the-past<=>btp but compound -> pc not 15 as pc is 1st
i7com = {} # combos e.g. opo = 3d and 4d
i7comord = defaultdict(lambda: defaultdict(int)) # ordered combos e.g. shuffling,roiling = 1,2 in stale tales slate
i7hfx = {} # header mappings e.g. ta to tables
i7f = {} # which header files apply to which projects e.g. shuffling has Nudges,Random Text,Mistakes,Tables
i7rn = {} # release numbers
i7nonhdr = {} # non header files e.g. story.ni, walkthrough.txt, notes.txt
i7triz = {} # there may be trizbort file name shifts e.g. shuffling -> shuffling-around
i7trizmaps = defaultdict(lambda:defaultdict(str)) # trizbort map sub-naming, mainly for Roiling
i7gbx = {} # geneeral binary extensions for debug, beta and release e.g. z6 goes to z8 z5 z5
i7pbx = {} # project binary extensions for debug, beta and release
i7binname = {} # binary nams e.g. roiling to A Roiling Original

i7bb = [] # list of bitbucket repos
i7gh = [] # list of github repos

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
            continue
        if ll.startswith("ghproj:"):
            i7gx[lla[1]] = lla[0]
            continue
        if ll.startswith("binext:"):
            for temp in lla[0].split(","):
                i7gbx[temp] = lla[1].split(",")
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
            i7f[l0p] = [ src(l0p) ]
            for q in l1:
                i7f[l0p].append(hdr(l0p, q))
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
