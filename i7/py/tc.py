# tc.py
#
# inform transcript cutter
#
# tc.py (optional file name) (output file name)
#
# * uses a wildcard
#

from shutil import copy
import glob
import os
import sys
import re
from collections import defaultdict

launch_after = False
write_edit_files = False
write_over = False
warn_too_many = False
make_html = False
launch_html = False
max_files = 1
cur_launched = 0
tran_fi = "transcripts.htm"
track_quotes = True
downloads = "c:/users/andrew/downloads"

quote_tracker = defaultdict(int)

def usage():
    print("l = launch HTML file, l# = maximum files to launch (1=default)")
    print("w = write edit-* files, wo = write over edit files")
    print("h = make HTML, hl = launch HTML--can be run without any files input")
    print("q = quote tracking, nq/qn = no quote tracking")
    print("* gives a wildcard for files. Otherwise, tc.py just processes files.")
    exit()

def out_name(x):
    if x.endswith('.txt'):
        return re.sub("\.txt$", "-comments.txt", x)
    else:
        return "comments-" + x

def edit_name(x):
    if x.startswith("edit"): return ''
    return os.path.dirname(x) + "edit-" + os.path.basename(x)

def in_transcript_dir(x):
    q = os.getcwd()
    if os.path.exists(os.path.join(q, x)): return True
    if os.path.exists(os.path.join(q, 'transcripts', x)): return True
    if os.path.exists(os.path.join(downloads, x)):
        move_from_downloads(x)
        return True
    return False

def move_from_downloads(wild_card):
    print("Looking for wild cards {} extensions .txt, .log".format(wild_card))
    x = os.getcwd()
    cwd = os.getcwd()
    if 'transcripts' in cwd:
        to_dir = cwd
    elif os.path.exists("transcripts"):
        to_dir = os.path.join(cwd, 'transcripts')
    else:
        sys.exit("Must be in directory with TRANSCRIPTS subdirectory or TRANSCRIPTS in its path.")
    x = glob.glob(os.path.join(downloads, "*.txt"))
    x.extend(glob.glob(os.path.join(downloads, "*.log")))
    y = [a for a in x if wild_card in a.lower()]
    if not len(y):
        sys.exit("No wild cards found for {}.".format(wild_card))
    else:
        temp = [os.path.basename(q) for q in y]
        print("Found {} wild cards to copy over: {}".format(len(temp), ', '.join(temp)))
    for f in y:
        outfile = os.path.join(to_dir, os.path.basename(f))
        try:
            os.rename(f, outfile)
            print("Successfully renamed", f, "to", outfile)
        except:
            print("Failed to rename", f, "to", outfile)
    sys.exit()

def to_output(f_i, f_o):
    f2 = open(f_o, "w")
    f2.write("#created with tc.py\n#\n")
    count = comments = lines_in_out_file = 0
    lines = []
    so_far = ""
    with open(f_i) as file:
        for (lc, line) in enumerate(file, 1):
            if line.count('"') % 2:
                if line not in quote_tracker:
                    quote_tracker[line.strip()] = lc
            if line.startswith('>'):
                if re.search("^> *[\*;]", line):
                    f2.write("=" * 50 + "Line " + str(lc) + "\n")
                    f2.write(so_far + line)
                    lines_in_out_file = lines_in_out_file + so_far.count('\n') + 2
                    lines.append(lines_in_out_file)
                    so_far = ""
                    comments = comments + 1
                else:
                    so_far = "(prev) " + line
                    if line != line.lower() and '>Start of a transcript of' not in line:
                        if line.startswith(">>"):
                            continue
                        print(f_i, lc, line.strip(), "may be a comment.")
                continue
            so_far = so_far + line
    if so_far != "":
        f2.write("ENDING TEXT")
        f2.write(so_far)
    if track_quotes:
        if len(quote_tracker):
            for x in sorted(quote_tracker, key=quote_tracker.get):
                print("Odd # of quotes at line {0}: {1}".format(quote_tracker[x], x))
        else:
            print("No lines found with odd # of quotes.")
    if comments:
        comwri = "{:d} total comments found ({:s}).".format(comments, ', '.join(map(str, lines)))
        print(comwri)
        f2.write("\n" + comwri + "\n")
    f2.close()

so_far = ""

the_glob = ""

count = 1

my_files = []

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg.startswith('-'): arg = arg[1:]
    if '*' in arg: the_glob = arg
    elif arg == 'l': launch_after = True
    elif arg.startswith('l'):
        launch_after = True
        try:
            max_files = int(arg[1])
        except:
            print("Need integer argument l#### for number of files to launch.")
    elif arg.startswith("d="):
        wild_card = arg[2:]
        move_from_downloads(wild_card)
    elif arg == 'w': write_edit_files = True
    elif arg == 'h': make_html = True
    elif arg == 'hl': launch_html = make_html = True
    elif arg == 'wo': write_over = write_edit_files = True
    elif arg == 'q': track_quotes = True
    elif arg == 'nq' or arg == 'qn': track_quotes = False
    elif arg == '?': usage()
    elif in_transcript_dir(arg):
        my_files.append(arg)
    else:
        print("Bad argument", arg)
        sys.exit()
    count = count + 1

if the_glob:
    my_files = my_files + glob.glob(the_glob)

if not len(my_files) and not launch_html and not make_html:
    print("No files/html commands specified. Use * to add them all, or specify them in the arguments. -? for usage.")

for mf in my_files:
    if not mf.lower().endswith('txt'): continue
    if 'comments' in mf:
        print(mf, "contains COMMENTS and is probably a file output by tc. Ignoring", os.path.basename(mf))
        continue
    if not os.path.exists(mf):
        print(mf, "does not exist, skipping.")
        if the_glob: print("Not sure what happened, since this was from a glob.")
    else:
        file_to_launch = ""
        if write_edit_files:
            ef = edit_name(mf)
            if ef:
                if os.path.exists(ef) and not write_over:
                    print(ef, "exists. Use (-)wo to write over.")
                    continue
                print("Edits:", mf, 'to', ef)
                copy(mf, ef)
                os.system("attrib -r " + ef)
                file_to_launch = ef
        else:
            ona = out_name(mf)
            print("Comments:", os.path.basename(mf), "to", os.path.basename(ona))
            if os.path.exists(ona):
                if write_over == False:
                    print(ona, "exists. Use -wo to write over.")
                    continue
                else:
                    print("Overwriting", ona)
                file_to_launch = ona
            to_output(mf, ona)
        if launch_after:
            if not file_to_launch:
                print("WARNING launch flag on but no file to launch", mf)
                continue
            if len(my_files) > cur_launched:
                print("Launching", file_to_launch)
                os.system(file_to_launch)
                cur_launched += 1
            else: warn_too_many = True

if make_html:
    h_ary = glob.glob("comments*") + glob.glob("*comments") + glob.glob("*comments.txt")
    hout = open(tran_fi, "w")
    hout.write("<html>\n<title>\nHTML list of transcripts</title>\n<body>\n")
    for h in h_ary:
        hout.write("<a href = {:s}>{:s}</a><br />\n".format(h, h))
    hout.write("</body>\n</html>\n")
    hout.close()

if launch_html: os.system(tran_fi)

if warn_too_many: print("Too many files to launch.")
