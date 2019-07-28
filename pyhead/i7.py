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
np_xml = 'C:/Users/Andrew/AppData/Roaming/Notepad++/session.xml'
f_dic = "c:/writing/dict/brit-1word.txt"
f_f = "c:/writing/dict/firsts.txt"
f_l = "c:/writing/dict/lasts.txt"
prt = "c:/games/inform/prt"
prt_temp = os.path.join(prt, "temp")
i7_cfg_file = "c:/writing/scripts/i7p.txt"
triz_dir = "c:\\games\\inform\\triz\\mine"
gh_dir = "c:\\users\\andrew\\documents\\GitHub"

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

def to_table(x):
    return re.sub(" *\[.*", "", line.lower().strip())

def is_outline_start(x, case_insensitive = True):
    return re.sub(outline_re, x)

oline = is_outline_start

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

def plur(a):
    return '' if a == 1 else 's'

def wm(x1, x2, ignore_if_identical = True):
    if ignore_if_identical and cmp(x1, x2):
        print("Not comparing identical files", x1, "and", x2)
        return
    os.system("wm \"{:s}\" \"{:s}\"".format(x1, x2))

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

def main_src(x):
    return os.path.normpath(os.path.join(sdir(x), "story.ni"))

proj_src = src = main_src

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

def hdr(x, y):
    return '{:s}\{:s} {:s}.i7x'.format(extdir, lpro(x, True).title(), i7hfx[y].title() if y in i7hfx else y.title())

hdrfile = hfile = hdr

def invis_file(x, warning=False):
    try_1 = "c:/writing/scripts/invis/{:s}.txt".format(i7xr[x] if x in i7xr.keys() else x)
    if os.path.exists(try_1): return try_1
    if warning: print("WARNING no invisiclues file for", x)
    return ""

def notes_file(x):
    return sdir(x) + "/" + "notes.txt"

def walkthrough_file(x):
    return sdir(x) + "/" + "walkthrough.txt"

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

def proj2dir(x):
    return "c:\\games\\inform\\{:s}.inform\\source".format(proj_exp(x))

sdir = p2d = proj2dir

def go_proj(x):
    os.chdir(proj2dir(x))
    return

go_p = proj_dir = to_proj = go_proj

def dir2proj(x = os.getcwd(), to_abbrev = False):
    x0 = x.lower()
    if os.path.exists(x0 + "\\story.ni") or ".inform" in x: # this works whether in the github or inform directory
        x2 = re.sub("\.inform.*", "", x0)
        x2 = re.sub(".*[\\\/]", "", x2)
        if "\\" in x2 or "/" in x2: return ""
        if to_abbrev and x2 in i7xr: return i7xr[x2]
        return x2
    elif re.search("documents.github..", x0):
        x2 = re.sub(".*documents.github.", "", x0, 0, re.IGNORECASE)
        x2 = re.sub("[\\\/].*", "", x2)
        if re.search("[a-z]", x2):
            if to_abbrev and x2 in i7xr: return i7xr[x2]
            return x2
        return ""
    else:
        return ""

sproj = d2p = dir2proj

npo = mt.npo

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

def all_proj_fi(x, bail = True):
    xp = i7xr[x] if x in i7xr.keys() else x
    if xp not in i7com.keys():
        if bail: raise("No full project named {:s}".format(x))
        return []
    ary = []
    for q in i7com[xp].keys(): ary += i7f[q]
    return ary

apf = all_proj_fi

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
        if ll.startswith("combo:"):
            i7com[lla[0]] = lla[1]
            subproj = lla[1].split(",")
            for x in range(0, len(subproj)):
                i7comord[lla[0]][subproj[x]] = x + 1
            continue
        if ll.startswith("ghproj:"):
            i7gx[lla[1]] = lla[0]
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

def triz_rooms(file_name):
    triz = defaultdict(str)
    try:
        e = ET.parse(file_name)
    except:
        print("Couldn't find", file_name)
        exit()
    root = e.getroot()
    for elem in e.iter('room'):
        if elem.get('name'):
            x = str(elem.get('name')).lower()
            x = re.sub(" *\(.*\)", "", x) # get rid of parenthetical/alternate name
            x = re.sub(",", "", x) # get rid of commas Inform source doesn't like
            stuf_ary = re.split(" */ *", x) # optional for if a room name changes
            for q in stuf_ary:
                triz[q] = str(elem.get('region')).lower()
        # print (x,triz[x])
        # triz[atype.get('name')] = 1;
    return triz

def _valid_i7m_arg(x):
    if x[0] == '-': x = x[1:];
    if '?' not in x: return False
    x = re.sub("\?", "", x)
    return re.search("^[rv]*$", x)

def rmbrax(my_str, spaces_too = True, end_only = False):
    regex_str = "\[[^\]]*\]"
    if spaces_too: regex_str = " *" + regex_str + " *"
    if end_only: regex_str += "$"
    my_str = re.sub(" *\[[^\]]*\] *", "", my_str)
    return my_str

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
