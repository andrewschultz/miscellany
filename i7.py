# i7.py
#
# basic dictionaries for various projects
#
# along with very basic python functions
#

from collections import defaultdict
import re
import os
import __main__ as main

np = "\"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\""

def open_source():
    npo(main.__file__)
    exit()

def src(x):
    return "c:\\games\\inform\\{:s}.inform\\source\\story.ni".format(x)

def triz(x):
    return "c:\\games\\inform\\triz\\mine\\{:s}.trizbort".format(x)

def hfile(x, y):
    x2 = re.sub("-", " ", x)
    return "C:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\{:s} {:s}.i7x".format(x2, y)

def sdir(x):
    return "c:\\games\\inform\\{:s}.inform\\source".format(x)

def dir2proj(x = os.getcwd()):
    if os.path.exists(x + "\\story.ni"):
        x2 = re.sub("\.inform.*", "", x)
        x2 = re.sub(".*[\\\/]", "", x2)
    if "\\" in x2 or "/" in x2: return ""
    return x2

def npo(my_file, my_line = 0, print_cmd = False):
    cmd = "start \"\" {:s} {:s} -n{:d}".format(np, my_file, my_line)
    if print_cmd: print("Launching", my_file, "at line", my_line, "in notepad++.")
    os.system(cmd)

def see_uniq_and_vers():
    i7rev = defaultdict(list)
    for x in i7x.keys():
        i7rev[i7x[x]].append(x)
    for y in sorted(i7rev.keys()):
        if len(i7rev[y]) == 1:
            # print(y, "is unique")
            if y in i7xr.keys():
                print(y, "doesn't need to be in i7xr.")
            else:
                print("Defining", y, "reverse to", i7rev[y][0])
                i7xr[y] = i7rev[y][0]
        else:
            # print(y, "is mapped to", len(i7rev[y]), "different values:", i7rev[y])
            if y not in i7xr.keys():
                print(y, "should be in i7xr, with", len(i7rev[y]), "different values.")
    for y in sorted(i7rev.keys()):
        if y not in i7rn.keys():
            print(y, "needs a release number or file name")

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

i7xd = "C:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\"

i7c = {
  "sts": ["roiling", "shuffling"],
  "ops": ["threediopolis", "fourdiopolis"],
  "as": ["slicker-city", "compound", "buck-the-past" ]
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
  "pu": "put-it-up",
  "up": "put-it-up",
  "sw": "spell-woken"
};

i7xr = { "shuffling": "sa",
  "roiling": "roi",
  "threediopolis": "3d",
  "fourdiopolis": "4d",
  "ugly-oafs": "uo",
  "compound": "pc",
  "slicker-city":"sc" ,
  "btp-st":"bs" ,
  "buck-the-past": "btp",
  "put-it-up": "pu",
  "molesworth": "mo"
};

i7f = {
  "shuffling": [
    "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling Nudges.i7x",
    "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling Random Text.i7x",
    "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling Mistakes.i7x",
    "c:\\games\\inform\\shuffling.inform\\source\\story.ni"
    ],
  "roiling": [
    "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling Nudges.i7x",
    "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling Random Text.i7x",
    "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling Mistakes.i7x",
    "c:\\games\\inform\\roiling.inform\\source\\story.ni"
    ],
    "buck-the-past": ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\buck the past tables.i7x", "c:\\games\\inform\\buck-the-past.inform\\source\\story.ni"],
    "compound": ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Compound tables.i7x", "c:\\games\\inform\\compound.inform\\source\\story.ni"],
    "slicker-city": ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\slicker city tables.i7x", "c:\\games\\inform\\slicker-city.inform\\source\\story.ni"],
    "spell-woken": ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\spell woken tables.i7x",
    "c:\\games\\inform\\spell-woken.inform\\source\\story.ni"],
    "put-it-up": ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Put it Up Tables.i7x",
    "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Put it Up Mistakes.i7x",
    "c:\\games\\inform\\put-it-up.inform\\source\\story.ni"]
  }

if "i7.py" in main.__file__:
    print("i7.py is a header file. It should not be run on its own.")
    print("Try running something else, instead.")
    # see_uniq_and_vers()
    exit()
