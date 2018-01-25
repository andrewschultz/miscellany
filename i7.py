# i7.py
#
# basic dictionaries for various projects

import os

np = "\"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\""

def src(x):
    return "c:\\games\\inform\\{:s}.inform\\source\\story.ni".format(x)

def sdir(x):
    return "c:\\games\\inform\\{:s}.inform\\source".format(x)

def npo(my_file, my_line, print_cmd = False):
    cmd = "start \"\" {:s} {:s} -n{:d}".format(np, my_file, my_line)
    if print_cmd: print("Launching", my_file, "at line", my_line, "in notepad++.")
    os.system(cmd)

i7xd = "C:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\"

i7rn = { "shuffling": "shuffling_around_release_5",
  "roiling": "4",
  "slicker-city": "2",
  "compound": "problems_compound_3",
  "fourdiopolis": "3",
  "threediopolis": "4",
  "buck-the-past": "1"
}

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
  "bs": "btp-st",
  "s17": "btp-st",
  "btp": "buck-the-past",
  "mo": "molesworth",
  "mw": "molesworth",
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
  "put-it-up": "pu"
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
    "put-it-up": ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\put it up tables.i7x",
    "c:\\games\\inform\\put-it-up.inform\\source\\story.ni"]
  }