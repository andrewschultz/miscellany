#
# mytools.py
#
# a bunch of auxiliary/helper scripts to make things easier

import re
import pyperclip
import sys
import os
import __main__ as main
from filecmp import cmp
from collections import defaultdict
from fractions import gcd
from functools import reduce
import subprocess

np_xml = 'C:/Users/Andrew/AppData/Roaming/Notepad++/session.xml'
np = "\"c:\\program files (x86)\\notepad++\\notepad++.exe\""
my_creds = "c:/coding/perl/proj/mycreds.txt"

title_words = ["but", "by", "a", "the", "in", "if", "is", "it", "as", "of", "on", "to", "or", "sic", "and", "at", "an", "oh", "for", "be", "not", "no", "nor", "into", "with", "from", "over"]

default_browser_exe = "c:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
file_post_list = defaultdict(lambda: defaultdict(int))

def bail_if_not(f, file_desc = ""):
    if not os.path.exists(f): sys.exit("Need {:s}{:s}file {:s}".format(file_desc, " " if file_desc else "", f))

def plur(a):
    return '' if a == 1 else 's'

def is_basename(a):
    return not ('/' in a or '\\' in a)

def temp_file_gen(file_name, my_dir = os.getcwd(), prefix="temp", before_extension = False):
    if not is_basename(file_name):
        return file_name
    if not before_extension:
        return os.path.join(my_dir, prefix + "-" + file_name)
    ary = list(os.path.splitext(file_name))
    ary[0] += "-" + prefix
    return os.path.join(my_dir, ''.join(ary))

def cheap_html(text_str, out_file = "c:/writing/temp/temp-htm.htm", title="HTML generated from text", launch = True):
	f = open(out_file, "w")
	f.write("<html>\n<title>{:s}</title>\n<body><\n><pre>\n{:s}\n</pre>\n</body>\n</html>\n".format(title, text_str))
	f.close()
	if launch: os.system(out_file)

def nohy(x): # mostly for command line argument usage, so -s is -S is s is S.
    if x[0] == '-': x = x[1:]
    return x.lower()

nohyp = noh = nohy

def is_anagram(x):
    q = defaultdict(int)
    y = re.sub("[^a-z]", "", x.lower())
    for j in y: q[j] += 1
    gc = reduce(gcd, q.values())
    return gc > 1

is_anagramy = is_anagrammy = is_anagram

def is_limerick(x, accept_comments = False): # quick and dirty limerick checker
    if accept_comments and '#lim' in x: return True
    if x.count('/') != 4: return False
    temp = re.sub(".* #", "", x)
    if len(x) > 120 and len(x) < 240: return True

is_limericky = is_limerick

def is_palindrome(x, accept_comments = False):
    if accept_comments and "#pal" in x: return True
    let_only = re.sub("[^a-z]", "", x.lower())
    return let_only == let_only[::-1]

is_palindromey = is_palindromy = is_palindrome

def clipboard_slash_to_limerick(print_it = False):
    x = slash_to_limerick(pyperclip.paste())
    if print_it: print(x)
    pyperclip.copy(x)
    return "!"

def slash_to_limerick(x): # limerick converter
    retval = ""
    for x0 in x.split("\n"):
        if "/" in x0:
            retval += "====\n" + re.sub(" *\/ ", "\n", x0) + "\n"
        else: retval += x0 + "\n"
    return retval.rstrip() + "\n"

def cfgary(x, delimiter="\t"): # A:b,c,d -> [b, c, d]
    if ':' not in x:
        print("WARNING, cfgary called on line without starting colon")
        return []
    temp = re.sub("^[^:]*:", "", x)
    return temp.split(delimiter)

def compare_unshuffled_lines(fpath1, fpath2): # true if identical, false if not
    with open(fpath1, 'r') as file1, open(fpath2, 'r') as file2:
        for linef1, linef2 in zip(file1, file2):
            linef1 = linef1.rstrip('\r\n')
            linef2 = linef2.rstrip('\r\n')
            if linef1 != linef2:
                return False
        return next(file1, None) == None and next(file2, None) == None

cu = cul = compare_unshuffled_lines

def compare_shuffled_lines(f1, f2, bail = False, max = 0, ignore_blanks = False): # true if identical, false if not
    freq = defaultdict(int)
    total = defaultdict(int)
    with open(f1) as file:
        for line in file:
            freq[line.lower().strip()] += 1
            total[line.lower().strip()] += 1
    with open(f2) as file:
        for line in file:
            freq[line.lower().strip()] -= 1
            total[line.lower().strip()] += 1
    difs = [x for x in freq if freq[x]]
    if ignore_blanks and '' in difs: difs.remove('')
    left = 0
    right = 0
    totals = 0
    if len(difs):
        for j in difs:
            if freq[j] > 0 : left += 1
            else: right += 1
            totals += 1
            if not max or totals <= max:
                print('Extra', j, "/", "{:d} of {:d} in {:s}".format(abs(freq[j]), total[j], os.path.basename(f1) if freq[j] > 0 else os.path.basename(f2)))
            elif max and totals == max + 1:
                print("Went over maximum of", max)
        print(os.path.basename(f1), "has", left, "but", os.path.basename(f2), "has", right)
        if len(difs) == 1 and difs[0] == '':
            print("ONLY BLANKS are different. You can run this function with ignore_blanks = True.")
        if bail:
            print("Compare shuffled lines is bailing on difference.")
            sys.exit()
        return False
    print("No shuffle-diffs")
    return True

csl = cs = compare_shuffled_lines

def npo(my_file, my_line = 1, print_cmd = True, bail = True):
    cmd = "start \"\" {:s} \"{:s}\" -n{:d}".format(np, my_file, my_line)
    if print_cmd: print("Launching {:s} at line {:d} in notepad++{:s}.".format(my_file, my_line, " and bailing" if bail else ""))
    os.system(cmd)
    if bail: exit()

def add_postopen_file_line(file_name, file_line, rewrite = False, reject_nonpositive_line = True, priority = 10):
    if file_line <= 0 and reject_nonpositive_line: return
    if rewrite or file_name not in file_post_list or priority not in file_post_list[file_name]:
        file_post_list[file_name][priority] = file_line

add_post = add_postopen = add_post_open = addpost = add_postopen_file_line

def postopen_files(bail_after = True, acknowledge_blank = False):
    if len(file_post_list):
        for x in file_post_list:
            m = max(file_post_list[x])
            npo(x, file_post_list[x][m], bail = False)
    elif acknowledge_blank:
        print("There weren't any files slated for opening/editing.")
    if bail_after: sys.exit()

def open_source(bail = True):
    npo(main.__file__)
    if bail: exit()

# can't use os as it is, well, an imported package
o_s = open_source

def open_source_config(bail = True):
    npo(re.sub("py$", "txt", main.__file__))
    if bail: exit()

oc = o_c = open_config = open_source_config

def create_temp_alf(file_1, file_2, comments, spaces):
    l = sorted(open(file_1).readlines())
    f2 = open(file_2, "w")
    for x in l:
        if spaces == False and not x.strip(): continue
        if comments == False and x.startswith("#"): continue
        f2.write(x)
    f2.close()

def alfcomp(x1, x2, bail = True, comments = True, spaces = False):
    a1 = "c:/writing/temp/alpha-1.txt"
    a2 = "c:/writing/temp/alpha-2.txt"
    print("Alphabetical comparison: {} vs {}".format(x1, x2))
    create_temp_alf(x1, a1, comments, spaces)
    create_temp_alf(x2, a2, comments, spaces)
    wm(a1, a2)
    os.remove(a1)
    os.remove(a2)
    if bail: sys.exit()

def wm(x1, x2, ignore_if_identical = True):
    if ignore_if_identical and cmp(x1, x2):
        print("Not comparing identical files", x1, "and", x2)
        return
    os.system("wm \"{:s}\" \"{:s}\"".format(x1, x2))

def abbrev(my_str, my_len):
    return my_str[:my_len] + "..." if len(my_str) > my_len else my_str

mult_diff_tracker = defaultdict(list)

def create_mult_diffs(orig_file, line_list, sort_it = True, bail=False):
    out_temp = "c:/writing/temp/multdelt.txt"
    new_list = sorted(line_list)
    out_temp_stream = open(out_temp, "w")
    with open(orig_file) as file:
        for (line_count, line) in enumerate(file, 1):
            while len(new_list) and line_count == new_list[0]:
                print("Modifying line", line_count)
                new_list.pop(0)
                line = "++++" + line
            out_temp_stream.write(line)
    out_temp_stream.close()
    wm(orig_file, out_temp)
    os.remove(out_temp)
    if bail: sys.exit()

def many_mult_diffs(file_list, bail=True):
    for f in file_list:
        create_mult_diffs(f, mult_diff_tracker[f])
    if bail: sys.exit()

def unshift_num(x):
    return x.replace('!', '1').replace('@', '2').replace('#', '3').replace('$', '4').replace('%', '5').replace('^', '6').replace('&', '7').replace('*', '8').replace('(', '9').replace(')', '0')

def print_ranges_of(x, default_thing = "numbers"): # given a list of integers, this prints consecutive integers e.g. 1,2,3,5,7,8 = 1-3 5 7-8
    x = sorted(x)
    last_in_range = -1
    last_range_start = -1
    the_string = ""
    num_ranges = 0
    for y in range(0, len(x)):
        if x[y] > last_in_range + 1:
            if last_in_range > last_range_start:
                the_string += "-{}".format(last_in_range)
            last_in_range = last_range_start = x[y]
            if len(the_string): the_string += ","
            the_string += " {}".format(x[y])
            num_ranges += 1
        elif x[y] == last_in_range + 1:
            last_in_range = x[y]
        else:
            sys.exit("Nonincreasing list. Bailing.")
    if last_in_range > last_range_start:
        the_string += "-{}".format(last_in_range)
    print("{} {} in {} ranges:".format(len(x), default_thing, num_ranges), the_string.strip())

def follow_link(x):
    temp = x
    count = 0
    while os.path.islink(temp):
        if count == 11: sys.exit("Failed to resolve symlink: {}".format(temp))
        temp = os.readlink(temp)
        count += 1
    return temp

fl = follow_link

def add_quotes_if_space(x):
    if x.startswith('"'): return x
    if ' ' in x: return '"{}"'.format(x)
    return x

def print_and_warn(x):
    print(x)
    sys.stderr.write("(STDERR)" + x + "\n")

paw = p_a_w = print_and_warn

ZAP_PAREN=1
ZAP_BRACKETS=2
ZAP_BRACES=3

def zap_trail_paren(x, paren_flags = ZAP_PAREN, start_bracket = "\(", end_bracket = "\)"):
    if paren_flags == ZAP_PAREN:
        start_brax = "\("
        end_brax = "\)"
    if paren_flags == ZAP_BRACKETS:
        start_brax = "\["
        end_brax = "\]"
    if paren_flags == ZAP_BRACES:
        start_brax = "\{"
        end_brax = "\}"
    y = re.sub(r" *{}.*{} *$".format(start_brax, end_brax), "", x)
    return y

def text_in_browser(file_name, print_action = True, bail=False):
    cmd = '\"{}\" \"{}\"'.format(default_browser_exe, file_name)
    if print_action: print("Opening {} with {}.".format(file_name, default_browser_exe))
    subprocess.call([default_browser_exe, file_name])
    if bail: sys.exit()

tib = t_i_b = text_in_browser

#####################################################basic main-program checking stuff

if os.path.basename(main.__file__) == "mytools.py":
    print("mytools.py is a header file. It should not be run on its own.")
    print("Try running something else with the line import i7, instead, or ? to run a test.")
    exit()
