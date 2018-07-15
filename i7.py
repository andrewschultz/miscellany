# i7.py
#
# basic dictionaries for various projects
#
# along with very basic python functions
#

from collections import defaultdict
import sys
import re
import os
import __main__ as main

np = "\"c:\\program files (x86)\\notepad++\\notepad++.exe\""
f_dic = "c:/writing/dict/brit-1word.txt"
f_f = "c:/writing/dict/firsts.txt"
f_l = "c:/writing/dict/lasts.txt"
prt = "c:\\games\\inform\\prt"

oo = [ 'off', 'on' ]

def open_source():
    npo(main.__file__)
    exit()

def plur(a):
    return '' if a == 1 else 's'

def wm(x1, x2):
    os.system("wm \"{:s}\" \"{:s}\"".format(x1, x2))

def remove_quotes(x):
    temp = re.sub("\"", "", x)
    temp = re.sub("\".*", "", x)
    return temp

rq = remove_quotes

def src(x):
    return sdir(x) + "/" + "story.ni"

def mistake_file(x):
    return 'c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\{:s} Mistakes.i7x'.format(lpro(x, True).title())

def hdr(x, y):
    return 'c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\{:s} {:s}.i7x'.format(lpro(x, True).title(), y.title())

def mistake_file(x):
    return 'c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\{:s} Mistakes.i7x'.format(lpro(x, True).title())

mifi = mistake_file

def table_file(x):
    return 'c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\{:s} Tables.i7x'.format(lpro(x, True).title())

tafi = table_file

def test_file(x):
    return 'c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\{:s} Tests.i7x'.format(lpro(x, True).title())

tefi = test_file

def triz(x):
    u = { "shuffling": "shuffling-around" }
    return "c:\\games\\inform\\triz\\mine\\{:s}.trizbort".format(x if x not in u.keys() else u[x])

def hfile(x, y):
    x2 = re.sub("-", " ", x)
    return "c:\\program files (x86)\\inform 7\\inform7\\extensions\\andrew schultz\\{:s} {:s}.i7x".format(x2, y)

def lpro(x, spaces=False):
    retval = ''
    if x in i7xr.keys(): retval = x
    elif x in i7x.keys(): retval = i7x[x]
    if spaces: retval = re.sub("-", " ", retval)
    return retval

def proj2dir(x):
    return "c:\\games\\inform\\{:s}.inform\\source".format(i7x[x] if x in i7x.keys() else x)

sdir = p2d = proj2dir

def go_proj(x):
    os.chdir(proj2dir(x))
    return

go_p = to_proj = go_proj

def dir2proj(x = os.getcwd()):
    if os.path.exists(x + "\\story.ni"):
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
    if xp not in i7c.keys():
        if bail: raise("No full project named {:s}".format(x))
        return []
    ary = []
    for q in i7c[xp].keys(): ary += i7f[q]
    return ary

apf = all_proj_fi

i7xd = "C:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\"

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
i7rn = { "shuffling": "shuffling_around_release_5",
  "roiling": "4",
  "slicker-city": "2",
  "compound": "problems_compound_3",
  "fourdiopolis": "3",
  "threediopolis": "4",
  "buck-the-past": "1"
}

# these are arranged roughly in order of completion/creation
i7x = { "12": "shuffling",
  "sa": "shuffling",
  "roi": "roiling",
  "s13": "roiling",
  "sts": "stale-tales-slate",
  "3": "threediopolis",
  "3d": "threediopolis",
  "13": "threediopolis",
  "14": "ugly-oafs",
  "oafs": "ugly-oafs",
  "s15": "dirk",
  "15": "compound",
  "pc": "compound",
  "4": "fourdiopolis",
  "4d": "fourdiopolis",
  "s16": "fourdiopolis",
  "16": "slicker-city",
  "sc": "slicker-city",
  "bs": "btp-st",
  "s17": "btp-st",
  "btp": "buck-the-past",
  "mo": "molesworth",
  "mw": "molesworth",
  "ai": "ailihphilia",
  "ail": "ailihphilia",
  "pu": "ailihphilia",
  "up": "ailihphilia",
  #"sw": "tragic-mix",
  "tm": "tragic-mix",
  "69": "69105more",
  "qb": "big-nose",
  "bn": "big-nose",
  "ss": "status-seeker",
  "as": "alec-smart",
  "ops": "opolis",
  "op": "opolis"
};

i7xr = { "shuffling": "sa",
  "roiling": "roi",
  "threediopolis": "3d",
  "fourdiopolis": "4d",
  "ugly-oafs": "uo",
  "compound": "pc",
  "slicker-city":"sc" ,
  "btp-st":"bs" ,
  "ailihphilia": "ai",
  "molesworth": "mo",
  "big-nose": "qb",
  "opolis": "op",
};

i7f = {
    "shuffling": [ hdr('sa', 'Nudges'), hdr('sa', 'Random Text'), mistake_file('sa'), src('sa') ],
    "roiling": [ hdr('roi', 'Nudges'), hdr('roi', 'Random Text'), mistake_file('roi'), src('roi') ],
    "buck-the-past": [ tafi('btp'), src('btp') ],
    "compound": [ tafi('pc'), src('pc') ],
    "slicker-city": [ tafi('sc'), src('sc') ],
    "spell-woken": [ tafi('sw'), src('sw') ],
    "ailihphilia": [ tafi('ai'), tefi('ai'), mifi('ai'), src('ai') ]
  }

def valid_arg(x):
    if x[0] == '-': x = x[1:];
    if '?' not in x: return False
    x = re.sub("\?", "", x)
    return re.search("^[rv]*$", x)

if "i7.py" in main.__file__:
    if len(sys.argv) > 1 and valid_arg(sys.argv[1]):
        see_uniq_and_vers(sys.argv[1])
        exit()
    print("i7.py is a header file. It should not be run on its own.")
    print("Try running something else with the line import i7, instead, or ? to run a test.")
    # see_uniq_and_vers()
    exit()
