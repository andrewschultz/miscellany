#
# mytw.py: my template writer
#
# This is for when Inform runs things through the Parchment template. THe output index.html isn't quite what I want.
# This checks for if everything is sane and then tweaks the lines that need tweaking.
# It's a bit hard-coded, but it works.
#
# usage: nothing needed in the right directory
#        mytw.py would tweak Ailihphilia's necessary web pages
#

from filecmp import cmp
import re
import os
from shutil import copy
import sys

import i7
import mytools as mt

def check_valid_path():
    if not os.path.exists("style.css"):
        sys.exit("No style.css found. Be sure you are releasing to parchment.")
    if not os.path.exists("play.html"):
        sys.exit("No play.html found. Be sure you are releasing to Parchment.")

def rewrite_css():
    in_gameport = ever_gameport = False
    orig_out_file = this_out_file = "style2.css"
    rewrite_file = os.path.exists(orig_out_file)
    if rewrite_file:
        this_out_file = "bak-" + this_out_file
    f = open(this_out_file, "w")
    with open("style.css") as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#gameport"):
                in_gameport = True
                ever_gameport = True
            if not line.strip():
                in_gameport = False
            if in_gameport:
                if line.strip().startswith("bottom:"):
                    f.write("\tbottom: 1.4em;\n")
                    continue
                elif line.strip().startswith("left:"):
                    f.write("\tleft: 1em;\n")
                    continue
            f.write(line)
    f.close()
    if rewrite_file:
        if cmp(orig_out_file, this_out_file):
            print("Everything is identical between this template export and last for {}.".format(orig_out_file))
        else:
            print("Copying over {} to {}.".format(this_out_file, orig_out_file))
        copy(this_out_file, orig_out_file)
        os.remove(this_out_file)
    if not ever_gameport:
        print("Didn't find #gameport in style.css.")
    else:
        print("Found #gameport in style.css.")

def rewrite_play():
    got_css = False
    orig_out_file = this_out_file = "play2.html"
    rewrite_file = os.path.exists(orig_out_file)
    if rewrite_file:
        this_out_file = "bak-" + this_out_file
    f = open(this_out_file, "w")
    with open("play.html") as file:
        for (line_count, line) in enumerate (file, 1):
            if re.search("<link.*style.css", line):
                got_css = True
                line = line.replace("style.css", "style2.css")
            f.write(line)
    f.close()
    if rewrite_file:
        if cmp(orig_out_file, this_out_file):
            print("Everything is identical between this template export and last for {}.".format(orig_out_file))
        else:
            print("Copying over {} to {}.".format(this_out_file, orig_out_file))
        copy(this_out_file, orig_out_file)
        os.remove(this_out_file)
    if not got_css:
        print("Found relevant css-change lines in play.html.")
    else:
        print("Didn't find relevant css-change lines in play.html.")

cmd_count = 1
got_one = False

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    temp = i7.proj2matr(arg)
    if temp:
        if got_one:
            sys.exit("Can't run two projects in one run.")
        print("Going to", temp)
        got_one = True
        os.chdir(temp)
    else:
        sys.exit("Invalid project specified.")
    cmd_count += 1

check_valid_path()
rewrite_css()
rewrite_play()
