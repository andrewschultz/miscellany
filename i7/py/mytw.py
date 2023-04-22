#
# mytw.py: my template writer
#
# This is for when Inform runs things through the Parchment template. THe output index.html isn't quite what I want.
# This checks for if everything is sane and then tweaks the lines that need tweaking.
# It's a bit hard-coded, but it works.
#
# "release along with the parchment interpreter"
# release to itch.io
#
# usage: nothing needed in the right directory
#        mytw.py ai would tweak Ailihphilia's necessary web pages
#
# todo: allow for default path
#

from filecmp import cmp
import re
import os
from shutil import copy
import sys

import i7
import mytools as mt

def check_web_components():
    if not os.path.exists("style.css"):
        sys.exit("No style.css found. Be sure you are releasing to Parchment.")
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
    got_container = False
    ignore_next = False
    ignore_ever = False
    orig_out_file = this_out_file = "play2.html"
    rewrite_file = os.path.exists(orig_out_file)
    if rewrite_file:
        this_out_file = "bak-" + this_out_file
    f = open(this_out_file, "w")
    with open("play.html") as file:
        for (line_count, line) in enumerate (file, 1):
            if '<div class="container">' in line:
                got_container = True
                f.write(line)
                ignore_next = True
                ignore_ever = True
                continue
            if re.search("<link.*style.css", line):
                got_css = True
                line = line.replace("style.css", "style2.css")
            if ignore_next:
                if line.strip() != "</div>":
                    continue
                ignore_next = False
            f.write(line)
    f.close()
    if rewrite_file:
        if cmp(orig_out_file, this_out_file):
            print("Everything is identical between this template export and last for {}.".format(orig_out_file))
        else:
            print("Copying over {} to {}.".format(this_out_file, orig_out_file))
        copy(this_out_file, orig_out_file)
        os.remove(this_out_file)
    if ignore_next:
        print("I got to the end of the file and was still ignoring text. This is a big bug.")
    if not ignore_ever:
        print("I didn't find any DIV CONTAINER text to ignore.")
    if got_css:
        print("Found relevant css-change lines in play.html.")
    else:
        print("Didn't find relevant css-change lines in play.html.")
    print("Was {}able to delete container code in play.html.".format('' if got_container else 'un'))

cmd_count = 1
got_one = False

param_project = ''

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    temp = i7.long_name(arg)
    if temp:
        if param_project:
            sys.exit("Can't run two projects in one run.")
        param_project = temp
        print("Choosing project", param_project)
    else:
        sys.exit("Invalid project specified.")
    cmd_count += 1

if not param_project:
    param_project = i7.dir2proj()
    if not param_project:
        x = os.getcwd()
        if 'beta' in x.lower():
            param_project = 'beta'
        else:
            sys.exit("Could not get project from current directory or find one from the command line.")

i7.go_proj(param_project, materials=True)

check_web_components()
rewrite_css()
rewrite_play()
