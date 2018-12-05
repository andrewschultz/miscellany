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

from collections import defaultdict
import sys
import re
import os
import glob
from filecmp import cmp
from shutil import copy
import __main__ as main

np = "\"c:\\program files (x86)\\notepad++\\notepad++.exe\""
f_dic = "c:/writing/dict/brit-1word.txt"
f_f = "c:/writing/dict/firsts.txt"
f_l = "c:/writing/dict/lasts.txt"
prt = "c:/games/inform/prt"
prt_temp = os.path.join(prt, "temp")
i7_cfg_file = "c:/writing/scripts/i7p.txt"

table_row_count = defaultdict(int)

outline_val_hash = { 'volume': 5, 'book': 4, 'part': 3, 'chapter': 2, 'section': 1 }
ovh = outline_val_hash
outline_val = sorted(outline_val_hash, key=outline_val_hash.get)
ov = outline_val

auth = "Andrew Schultz"

on_off = [ 'off', 'on' ]
oo = on_off

smart = "c:/writing/smart.otl"
spoon = "c:/writing/spopal.otl"

extdir = r'c:\Program Files (x86)\Inform 7\Inform7\Extensions\{:s}'.format(auth)

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

def open_source():
    npo(main.__file__)
    exit()

# can't use os as it is, well, an imported package
o_s = open_source

def open_source_config():
    npo(re.sub("py$", "txt", main.__file__))
    exit()

oc = o_c = open_config = open_source_config

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

def wm(x1, x2):
    os.system("wm \"{:s}\" \"{:s}\"".format(x1, x2))

def remove_quotes(x):
    temp = re.sub("\"", "", x)
    temp = re.sub("\".*", "", x)
    return temp

rq = remove_quotes

def main_src(x):
    return os.path.normpath(os.path.join(sdir(x), "story.ni"))

src = main_src

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
    return '{:s}\{:s} {:s}.i7x'.format(extdir, lpro(x, True).title(), y.title())

hfile = hdr

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
    u = { "shuffling": "shuffling-around" }
    return "c:\\games\\inform\\triz\\mine\\{:s}.trizbort".format(x if x not in u.keys() else u[x])

def hf_exp(x, return_nonblank = True):
    xl = x.lower()
    if xl in i7hfx.keys(): return i7hfx[xl].title()
    if xl in i7hfx.values(): return xl.title()
    else: return xl.title()

th_exp = hf_exp

def proj_exp(x, return_nonblank = True, to_github = False):
    if to_github and x in i7gx.keys(): return i7gx[x]
    if x in i7xr.keys(): return x
    elif x in i7x.keys(): return i7x[x]
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

def proj2dir(x):
    return "c:\\games\\inform\\{:s}.inform\\source".format(proj_exp(x))

sdir = p2d = proj2dir

def go_proj(x):
    os.chdir(proj2dir(x))
    return

go_p = proj_dir = to_proj = go_proj

def dir2proj(x = os.getcwd()):
    if os.path.exists(x + "\\story.ni") or ".inform" in x:
        x2 = re.sub("\.inform.*", "", x)
        x2 = re.sub(".*[\\\/]", "", x2)
        if "\\" in x2 or "/" in x2: return ""
        return x2
    return ""

sproj = d2p = dir2proj

def npo(my_file, my_line = 1, print_cmd = True, bail = True):
    cmd = "start \"\" {:s} \"{:s}\" -n{:d}".format(np, my_file, my_line)
    if print_cmd: print("Launching {:s} at line {:d} in notepad++{:s}.".format(my_file, my_line, " and bailing" if bail else ""))
    os.system(cmd)
    if bail: exit()

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
i7hfx = {} # header mappings e.g. ta to tables
i7f = {} # which header files apply to which projects e.g. shuffling has Nudges,Random Text,Mistakes,Tables
i7rn = {} # release numbers
i7nonhdr = {} # non header files e.g. story.ni, walkthrough.txt, notes.txt

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
        if ll.startswith("combo:"):
            i7com[lla[0]] = lla[1]
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

def _valid_i7m_arg(x):
    if x[0] == '-': x = x[1:];
    if '?' not in x: return False
    x = re.sub("\?", "", x)
    return re.search("^[rv]*$", x)

if "i7.py" in main.__file__:
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
