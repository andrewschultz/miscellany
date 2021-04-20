#
# mytools.py
#
# a bunch of auxiliary/helper scripts to make things easier

import pathlib
import glob
import ctypes
import time
import re
import pyperclip
import sys
import os
import __main__ as main
from filecmp import cmp
from collections import defaultdict
from math import gcd
from functools import reduce
import subprocess
from shutil import copy
import xml.etree.ElementTree as ET
import codecs

np_xml = 'C:/Users/Andrew/AppData/Roaming/Notepad++/session.xml'

my_creds = "c:/coding/perl/proj/mycreds.txt"

title_words = ["but", "by", "a", "the", "in", "if", "is", "it", "as", "of", "on", "to", "or", "sic", "and", "at", "an", "oh", "for", "be", "not", "no", "nor", "into", "with", "from", "over"]

file_post_list = defaultdict(lambda: defaultdict(int))
file_extra_edit = defaultdict(lambda: defaultdict(int))

daily_wildcard = "20*.txt"

def dailies_of(my_dir):
    return [os.path.basename(x) for x in glob.glob(my_dir + "/" + daily_wildcard)]

def progfile_of(my_path):
    if os.path.exists(my_path):
        return my_path
    path_array = os.path.normpath(my_path).split(os.sep)
    if ' (x86)' not in path_array[1]:
        path_array[1] += ' (x86)'
    else:
        path_array[1] = path_array[1].replace(' (x86)', '')
    if os.path.exists(os.sep.join(path_array)):
        return os.sep.join(path_array)
    return my_path

default_browser_exe = progfile_of("c:\\Program Files\\Mozilla Firefox\\firefox.exe")

npnq = progfile_of("c:\\program files\\notepad++\\notepad++.exe")
np = '"{}"'.format(npnq)

def on_off(my_truth_state):
    return "on" if my_truth_state else "off"

def truth_state_of(text_data, print_warning = True):
    tl = text_data.lower()
    if tl == 'true' or tl == '1' or tl == 'yes': return True
    if tl == 'false' or tl == '0' or tl == 'no': return True
    if print_warning:
        print("Bad truth state:", text_data)
    return -1

def bail_if_not(f, file_desc = ""):
    if not os.path.exists(f): sys.exit("Need {:s}{:s}file {:s}".format(file_desc, " " if file_desc else "", f))

def plur(a, choices=['s', '']):
    if type(a) == list:
        a = len(a)
    return choices[a == 1]

def is_are(a):
    return plur(a, ['is', 'are'])

def no_quotes(a):
    return a.replace('"', '')

def letters_only(my_word, accept_hyphens=True):
    my_word = re.sub("[^a-zA-Z -]", "", my_word)
    if not accept_hyphens:
        my_word.replace("-", "")
    return my_word

noquotes = no_quo = noquo = no_quotes

def only_certain_letters(letter_list, string_to_search):
    if any(x not in letter_list for x in string_to_search):
        return False
    if len(string_to_search) == 0:
        return False
    return True

def is_basename(a):
    return not ('/' in a or '\\' in a)

def is_daily(x):
    if '/' in x or '\\' in x:
        x = os.path.basename(x).lower()
    return re.search("^2[0-9]{7}\.txt$", x)

def has_uncommented_text(x, bail_on_semicolon = False):
    if not exist(x): return False
    with codecs.open(x, errors='ignore') as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"): continue
            if bail_on_semicolong and line.startswith(";"): break
            if not line.strip(): return True
    return False

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

def num_value_from_text(my_line, my_index = 0):
    nums = re.findall("[0-9]+", my_line)
    try:
        return int(nums[my_index])
    except:
        return 0

def nohy(x): # mostly for command line argument usage, so -s is -S is s is S.
    if x[0] == '-': x = x[1:]
    return x.lower()

nohyp = noh = nohy

def decimal_only(val, digits = 3):
    fmt = "%.{}f".format(digits)
    ret = fmt % val
    if ret.startswith("0."):
        return ret[1:]
    if ret.startswith("-0."):
        return "-" + ret[2:]
    return ret

def is_npp_modified(my_file): # see if a file is unsaved in notepad++
    e = ET.parse(np_xml)
    for elem in e.iter('File'):
        this_np_file = elem.get("filename")
        if not os.path.exists(this_np_file): continue
        if my_file.lower() not in this_np_file.lower(): continue # this speeds stuff up slightly
        if os.path.samefile(this_np_file, os.path.abspath(my_file)):
            bfp = elem.get("backupFilePath")
            if bfp:
                if os.path.exists(bfp):
                    return True
            return False

def is_anagram(x, accept_comments = True, check_sections = True, wipe_author = True, ignore_leading_articles = True):
    article_string = r'^(a|an|the) '
    if ignore_leading_articles and re.search(article_string, x):
        if is_anagram(re.sub(article_string, "", x, re.IGNORECASE), accept_comments, check_sections, wipe_author, ignore_leading_articles):
            return True
    x = re.sub("#.*", "", x)
    if wipe_author: # for book titles for Roiling
        x = re.sub("\[r\], +by +", "", x, re.IGNORECASE)
    q = defaultdict(int)
    y = re.sub("[^a-z]", "", x.lower())
    if not y: return False
    for j in y: q[j] += 1
    gc = reduce(gcd, q.values())
    if gc == 1:
        return False
    if not check_sections:
        return True
    chunk_size = len(y) // gc
    first_chunk = sorted(y[0:chunk_size])
    for x in range (1, gc):
        this_chunk = sorted(y[x * chunk_size:(x+1) * chunk_size])
        if this_chunk != first_chunk:
            return False
    return True

is_anagramy = is_anagrammy = is_anagram

def is_limerick(x, accept_comments = False): # quick and dirty limerick checker
    if accept_comments and '#lim' in x: return True
    if x.count('/') != 4: return False
    temp = re.sub(".* #", "", x)
    if len(x) > 120 and len(x) < 240: return True

is_limericky = is_limerick

def is_palindrome(x, accept_comments = True):
    if accept_comments and "#pal" in x: return True
    if accept_comments: x = re.sub('#.*', '', x)
    let_only = re.sub("[^a-z]", "", x.lower())
    if not let_only: return False # blank strings don't work
    return let_only == let_only[::-1]

is_palindromey = is_palindromy = is_palindrome

def print_and_to_clip(my_str):
    print(my_str, end='')
    pyperclip.copy(my_str)

pc = print_and_to_clip

def clipboard_slash_to_limerick(print_it = False):
    x = slash_to_limerick(pyperclip.paste())
    if print_it: print(x)
    pyperclip.copy(x)
    return "!"

def slash_to_limerick(x): # limerick converter
    retval = ""
    for x0 in x.split("\n"):
        if "/" in x0:
            retval += "====\n" + re.sub(" *\/ *", "\n", x0) + "\n"
        else: retval += x0 + "\n"
    return retval.rstrip() + "\n"

def chop_front(x, delimiter="[:=]"):
    return re.sub(r'^.*?{}'.format(delimiter), '', x)

def no_colon(x):
    return chop_front(x, ':')

def no_equals(x):
    return chop_front(x, '=')

def cfgary(x, delimiter="\t"): # A:b,c,d -> [b, c, d] # deprecated for cfg_data_split below
    if ':' not in x:
        print("WARNING, cfgary called on line without starting colon")
        return []
    temp = re.sub("^[^:]*:", "", x)
    return temp.split(delimiter)

def cfg_data_split(x, delimiter=":=", to_tuple = True, strip_line = True):
    if strip_line:
        x = x.strip()
    ary = re.split("[{}]".format(delimiter), x, 1)
    if to_tuple:
        return(ary[0], ary[1])
    return ary

def is_properly_sectioned(my_file):
    in_section = False
    found_errors = False
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"): continue
            if not line.strip():
                in_section = False
                continue
            if line.startswith("\\"):
                if in_section:
                    print("Bad double-section at line {}.".format(line_count))
                    found_errors += 1
                in_section = True
            else:
                if not in_section:
                    print("Line without section at line {}.".format(line_count))
                    found_errors += 1
    return found_errors

def compare_unshuffled_lines(fpath1, fpath2): # true if identical, false if not
    with open(fpath1, 'r') as file1, open(fpath2, 'r') as file2:
        for linef1, linef2 in zip(file1, file2):
            linef1 = linef1.rstrip('\r\n')
            linef2 = linef2.rstrip('\r\n')
            if linef1 != linef2:
                return False
        return next(file1, None) == None and next(file2, None) == None

cu = cul = compare_unshuffled_lines

def compare_alphabetized_lines(f1, f2, bail = False, max = 0, ignore_blanks = False, verbose = True): # true if identical, false if not
    if verbose:
        print("Comparing alphabetized lines: {} vs {}.".format(f1, f2))
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
        for j in sorted(difs):
            if freq[j] > 0 : left += 1
            else: right += 1
            totals += 1
            if not max or totals <= max:
                print(">>>>RIGHT FILE" if freq[j] > 0 else "LEFT FILE<<<<", 'Extra line', "<blank>" if not j else j, "/", "{:d} of {:d} in {:s}".format(abs(freq[j]), total[j], os.path.basename(f1) if freq[j] > 0 else os.path.basename(f2)))
            elif max and totals == max + 1:
                print("Went over maximum of", max)
        print("{} has {} extra mismatches but {} has {}.".format(os.path.basename(f1), left, os.path.basename(f2), right))
        if len(difs) == 1 and difs[0] == '':
            print("ONLY BLANKS are different. You can run this function with ignore_blanks = True.")
        if bail:
            print("Compare shuffled lines is bailing on difference.")
            sys.exit()
        return False
    if verbose:
        print("No shuffle-diffs")
    return True

cs = ca = compare_shuffled_lines = cal = calf = compare_alphabetized_lines

def npo(my_file, my_line = 1, print_cmd = True, bail = True, follow_open_link = True, print_full_path = False):
    if not os.path.exists(my_file):
        print("WARNING:", my_file, "does not exist.")
    elif follow_open_link:
        my_file = follow_link(my_file)
        if not os.path.exists(my_file):
            print("WARNING: linked-to file", my_file, "does not exist.")
    if os.path.exists(my_file):
        cmd = "start \"\" {:s} \"{:s}\" -n{:d}".format(np, my_file, my_line)
        if print_cmd: print("Launching {:s} at line {:d} in notepad++{:s}.".format(my_file if print_full_path else os.path.basename(my_file), my_line, " and bailing" if bail else ""))
        os.system(cmd)
    if bail: exit()

def open_this(bail = True):
    try:
        npo(main.__file__, bail=bail)
    except Exception as e:
        print("Could not open source", main.__file__)
        print("Error thrown:")
        print(e)
        if bail:
            exit()

def add_postopen_file_line(file_name, file_line = 1, rewrite = False, reject_nonpositive_line = True, priority = 10):
    if file_line <= 0 and reject_nonpositive_line: return
    if file_name in file_post_list:
        try:
            file_extra_edit[file_name] += 1
        except:
            file_extra_edit[file_name] = 1
    if rewrite or file_name not in file_post_list or priority not in file_post_list[file_name]:
        file_post_list[file_name][priority] = file_line

add_open = add_post = add_postopen = add_post_open = addpost = add_postopen_file_line

def postopen_files(bail_after = True, acknowledge_blank = False, max_opens = 0, sleep_time = 0.1):
    if len(file_post_list):
        l = len(file_post_list)
        count = 0
        for x in file_post_list:
            if max_opens and count == max_opens:
                print("Reached max_opens of", max_opens, "so I am cutting it off here.")
                break
            m = max(file_post_list[x])
            bnx = os.path.basename(x)
            if x in file_extra_edit:
                print(file_extra_edit[x], "total extra edits for", bnx)
            el = len(file_post_list[x])
            if el > 1:
                print("Errors of {} different priorities were found in {}, so the first/last one may not be flagged. Just the most important one.".format(el, bnx))
            npo(x, file_post_list[x][m], bail = False)
            count += 1
            if count < 0:
                time.sleep(sleep_time)
    elif acknowledge_blank:
        print("There weren't any files slated for opening/editing.")
    if bail_after: sys.exit()

post_open = postopen = postopen_files

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

def strip_punctuation(q, zap_bounding_apostrophe = False):
    q = q.replace('"', '')
    if zap_bounding_apostrophe:
        q = re.sub("(\b'|'\b)", "", q)
    q = q.replace('.', '')
    q = q.replace(',', '')
    q = q.replace('-', ' ')
    q = ' '.join(q.split(' '))
    q = re.sub("^(an|the|a) ", "", q).strip()
    return q

def alphabetize_lines(x, ignore_punctuation_and_articles = True):
    if type(x) == str:
        temp = x.split("\n")
    return "\n".join(sorted(temp, key=lambda x:strip_punctuation(x) if ignore_punctuation_and_articles else x.lower())) + "\n"

def alfcomp(x1, x2, bail = True, comments = True, spaces = False, show_winmerge = True, acknowledge_comparison = True):
    a1 = "c:/writing/temp/alpha-1.txt"
    a2 = "c:/writing/temp/alpha-2.txt"
    if acknowledge_comparison:
        print("Alphabetical comparison: {} vs {}".format(x1, x2))
    create_temp_alf(x1, a1, comments, spaces)
    create_temp_alf(x2, a2, comments, spaces)
    if show_winmerge:
        wm(a1, a2)
        os.remove(a1)
        os.remove(a2)
        if bail: sys.exit()
    return cmp(a1, a2)

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
    if temp.startswith("\\\\?\\"):
        temp = temp[4:]
    return temp

fl = follow_link

def last_mod(x):
    x = follow_link(x)
    return os.stat(x).st_mtime

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

def first_word_of(x, allow_dashes = False, additional_chars = ""):
    valid_chars = "a-zA-Z"
    x = x.replace('"', '')
    if additional_chars:
        valid_chars += additional_chars
    elif allow_dashes:
        valid_chars += "-"
    my_regex = r'[^{}].*'.format(valid_chars)
    return re.sub(my_regex, "", x, 0, re.IGNORECASE)

first_word = first_word_of

def text_in_browser(file_name, print_action = True, bail=False):
    #obsolete -- subprocess launches Firefox without hogging the command line
    # cmd = 'start \"\" \"{}\" \"file:///{}\"'.format(default_browser_exe, file_name)
    if print_action: print("Opening {} with {}.".format(file_name, default_browser_exe))
    print(default_browser_exe, pathlib.Path(file_name).as_uri())
    subprocess.call([default_browser_exe, pathlib.Path(file_name).as_uri()])
    if bail: sys.exit()

tib = t_i_b = text_in_browser

def comment_combine(my_lines, cr_at_end = True):
    if type(cr_at_end) != bool and type(cr_at_end) != int:
        raise ValueError('You probably sent a couple strings instead of an array of strings: <<{} / {}>>'.format(my_lines, cr_at_end)) from None
    uncomment = ""
    comment = ""
    any_comment = False
    for x in my_lines:
        if '#' in x:
            any_comment = True
        else:
            uncomment += " " + x.strip()
            continue
        comment_array = x.strip().split("#", 1)
        uncomment += " " + comment_array[0].strip()
        if comment: comment += " / "
        comment += comment_array[1].strip()
    if any_comment:
        uncomment += " # " + comment
    if cr_at_end:
        uncomment += "\n"
    return uncomment.lstrip()

comcom = comment_combine

def zap_comment(my_line, zap_spaces_before = True):
    substring = "#.*"
    if zap_spaces_before: substring = ' *' + substring
    return re.sub(substring, "", my_line)

no_comment = no_comments = zap_comments = zap_comment

def null_of(null_truth_state):
    return subprocess.DEVNULL if null_truth_state else None

def uncommented_length(x):
    return len(zap_comment(x))

def print_status_of(my_file):
    if not os.path.exists(my_file):
        print(my_file, "does not exist.")
    elif os.stat(my_file).st_size == 0:
        print(my_file, "is zero bytes.")
    else:
        print(my_file, "appears to have been created okay.")

def is_posneg_int(x, allow_zero = False):
    try:
        q = int(x)
        return allow_zero or q
    except:
        pass
    return False

def print_and_run(x, print_command_being_run = True):
    if print_command_being_run: print(x)
    os.system(x)

def subproc_and_run(x, print_command_being_run = True, need_successful_return = False, null_stdout = True, null_stderr = False):
    if print_command_being_run: print("RUNNING:", ' '.join(x))
    if need_successful_return:
        subprocess.check_call(x)
    else:
        subprocess.call(x, stdout=null_of(null_stdout), stderr=null_of(null_stderr))

def delete_task(my_cmd):
    my_cmd = "schtasks /delete /f /tn {}"
    print_and_run(my_cmd)

def set_task(task_name, task_to_run, task_time, task_date):
    my_cmd = "schtasks /f /create /sc ONCE /tn {} /tr {} /st {} /sd {}".format(task_name, task_to_run, task_time, task_date)
    print_and_run(my_cmd)

def latest_of(file_array, latest = True):
    new_ret = ''
    last_time = 0
    for x in file_array:
        try:
            y = os.stat(x)
            if y.st_mtime > last_time:
                new_ret = x
        except:
            print("No info for", x)
    if not new_ret: sys.exit("Can't get latest of {}".format(', '.join(file_array)))
    return new_ret

def first_of(file_array, latest = True):
    new_ret = ''
    first_time = time.time()
    for x in file_array:
        try:
            y = os.stat(x)
            if y.st_mtime < first_time:
                new_ret = x
        except:
            print("No info for", x)
    if not new_ret: sys.exit("Can't get first of {}".format(', '.join(file_array)))
    return new_ret

def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

is_admin = admin = isadmin = Admin = isAdmin

#####################################################basic main-program checking stuff

if os.path.basename(main.__file__) == "mytools.py":
    print("mytools.py is a header file. It should not be run on its own.")
    print("Try running something else with the line import i7, instead, or ? to run a test.")
    exit()
