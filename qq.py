################################
# qq.py
#
# finds all possible TODO
#
# supersedes qq.pl

import re
import os
import sys
import i7
from collections import defaultdict

def usage():
    print("-a = search all files.")
    print("-h = export to HTML, -ha = search all.")
    print("-v = verbose")
    print("-b = bail on first")
    print("-l = open last line")
    print("-m = minimum line to open (no space) (no need for number)")
    print("-x = maXimum line to open (no space)")
    print("-nl = no launch")
    print("-o = bail once over # lines (no space)")
    exit()

def found_todo_text(ll):
    if re.search("\[[^\]]*(\?\?|\btodo).*\]", ll): return True
    if re.search("too-generic", ll) and "\t" not in ll: return True
    return False

def file_hunt(x):
    # print("HUNTING TODOS in", x)
    bad_lines = []
    any_yet = False
    ignored = []
    with open(x) as file:
        for (line_count, line) in enumerate(file, 1):
            ll = line.lower()
            if found_todo_text(ll):
                if max_line and line_count > max_line:
                    if verbose: print("Ignoring match above line", max_line, "at line", line_count, ":", line.strip())
                    ignored.append(line_count)
                    continue
                if line_count > min_line:
                    if html_exp and not any_yet:
                        fhtml.write("<font size=+3 color=red>TODO RESULTS IN {:s}</font><br />\n".format(x))
                        any_yet = True
                    bad_lines.append(line_count)
                    verbose_detail = "Line {:d}, instance {:d}, -- {:s}".format(line_count, len(bad_lines), line.strip())
                    if verbose: print(verbose_detail)
                    if html_exp:
                        fhtml.write(verbose_detail + "<br />\n")
                else:
                    if verbose: print("Ignoring match below line", min_line, "at line", line_count, ":", line.strip())
                    ignored.append(line_count)
    if any_yet == False and html_exp: fhtml.write("<font size=+3 color=green>NOTHING FOUND {:s}</font><br />\n".format(x))
    if len(bad_lines) == 0:
        print("Nothing found for", x)
        print()
        return
    local_bail = len(bad_lines) - 1 if last_line_open else min(bail_num, len(bad_lines)-1)
    if not verbose: print("      ", len(bad_lines), "total instances found for", x, ":", ', '.join(str(x) for x in bad_lines))
    if launch_first_find:
        cmd = "start \"\" {:s} \"{:s}\" -n{:d}".format(i7.np, x, bad_lines[local_bail])
        os.system(cmd)
    print()
    if len(ignored): print("Ignored lines:", ', '.join([str(x) for x in ignored]))
    return len(bad_lines) > 0 # If we got a ??, return true

def todo_hunt(x):
    x2 = i7.main_src(x)
    if x not in i7.i7f.keys():
        print("WARNING i7.py doesn't define a file list for", x, "so I'm just going with story.ni.")
        return file_hunt(x2) and bail_on_first
    x3 = re.sub(r'\\', "/", x2)
    if x2 not in i7.i7f[x] and x3 not in i7.i7f[x]:
        print("WARNING you should maybe have the story.ni file in the i7.py list. I am adding it to what to check.")
        if file_hunt(x2) and bail_on_first: return True
    else:
        print("TRIVIAL CHECK PASSED: story.ni file is in i7.py list...")
    for y in i7.i7f[x]:
        if file_hunt(y) and bail_on_first: return True
    return False

# options
last_line_open = False
bail_on_first = True
launch_first_find = True
search_all_qs = False
verbose = False
bail_num = 0
min_line = 0
max_line = 0
html_exp = False

# variables
searchables = []

if len(sys.argv) > 1:
    count = 1
    while count < len(sys.argv):
        ll = sys.argv[count].lower()
        if ll.startswith("-"):
            print("WARNING:", ll, "does not need dash, eliminating.")
            ll = ll[1:]
        if ll == 'a':
            search_all_qs = True
            launch_first_find = False
            verbose = False
        elif ll == 'v':
            verbose = True
        elif ll == 'nl':
            launch_first_find = False
        elif ll == 'b':
            bail_on_first = True
        elif ll == 'h':
            html_exp = True
            launch_first_find = False
            bail_on_first = False
        elif ll == 'ha':
            html_exp = True
            launch_first_find = False
            search_all_qs = True
            bail_on_first = False
        elif ll == 'l':
            last_line_open = True
        elif ll == '?':
            usage()
            exit()
        elif ll.isdigit(): min_line = int(ll)
        elif ll.startswith('m'):
            try:
                min_line = int(ll[1:])
            except:
                print("The m (minimum line) option requires a number right after: no spaces.")
        elif ll.startswith('x'):
            try:
                max_line = int(ll[1:])
            except:
                print("The m (minimum line) option requires a number right after: no spaces.")
        elif ll.startswith('o'):
            try:
                bail_num = int(ll[1:])
            except:
                print("The o (bail over #) option requires a number right after: no spaces.")
        elif ll in i7.i7x.keys():
            searchables.append(i7.i7x[ll])
        elif ll in i7.i7x.values():
            searchables.append(ll)
        else:
            print("WARNING!", ll, "is not in i7x.keys.")
        count += 1

if min_line and max_line and max_line < min_line: sys.exit("Maximum line must be greater than minimum line. You've defined min={:d} max={:d}.".format(min_line, max_line))

html_file = "c:/games/inform/qq.htm"

if html_exp:
    fhtml = open(html_file, "w")
    fhtml.write("<html>\n<title>\nQQ.PY all-project results</title>\n<body>\n")

if search_all_qs:
    for x in sorted(i7.i7xr):
        todo_hunt(x)
elif len(searchables) == 0:
    if os.path.exists("story.ni"):
        todo_hunt(i7.dir2proj(os.getcwd()))
    else:
        sys.exit("Didn't find any story.ni to process. Bailing.")
else:
    for x in sorted(searchables):
        todo_hunt(x)

if html_exp:
    fhtml.write("</body>\n</html>\n")
    fhtml.close()
    print("Launching", html_file)
    os.system(html_file)
