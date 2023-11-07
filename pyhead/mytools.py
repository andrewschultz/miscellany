#
# mytools.py
#
# a bunch of auxiliary/helper scripts to make things easier

import stat
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
import colorama
import pendulum
import traceback

mt_default_dict = defaultdict(str)

TXT = WTXT = RESET = colorama.Style.RESET_ALL
RESETCR = CRRESET = RESET + "\n"
WARN = WARNED = CAUTION = colorama.Fore.YELLOW
FAIL = FAILED = ERROR = STOP = colorama.Fore.RED
SUCCESS = SUCCEED = PASS = OKAY = GO = colorama.Fore.GREEN

########################string constants

gh_dir = gitbase = 'c:\\users\\andrew\\documents\\github'
config_dir = os.path.join(gh_dir, "configs")
notes_dir = os.path.join(config_dir, "notes")

np_xml = 'C:/Users/Andrew/AppData/Roaming/Notepad++/session.xml'

my_creds = "c:/coding/perl/proj/mycreds.txt"

hosts_file = "C:/Windows/System32/drivers/etc/hosts"

title_words = ["but", "by", "a", "the", "in", "if", "is", "it", "as", "of", "on", "to", "or", "sic", "and", "at", "an", "oh", "for", "be", "not", "no", "nor", "into", "with", "from", "over"]

words_file = 'c:/writing/dict/brit-1word.txt'
first_name_file = 'c:/writing/dict/firsts.txt'
last_name_file = 'c:/writing/dict/lasts.txt'

file_post_list = defaultdict(lambda: defaultdict(int))
file_extra_edit = defaultdict(lambda: defaultdict(int))

daily_wildcard = "20*.txt"

daily_warning_bumper = "**MODIFY DAILY INSTEAD(?)\n"
daily_warning_bumper_nolb = daily_warning_bumper.strip()
daily_warning_bumper_short = "**MODIFY"

########################date constants

this_year = pendulum.now().year
initial_date = pendulum.from_timestamp(0, tz='local')

########################numerical constants

DASH_TO_UNDERSCORE = 1
KEEP_DASH_UNDERSCORE = 0
UNDERSCORE_TO_DASH = -1

SORT_ALPHA_BACKWARD = -1
SORT_ALPHA_NONE = 0
SORT_ALPHA_FORWARD = 1


def dailies_of(my_dir = "c:/writing/daily", full_file_path = False):
    try_1 = glob.glob(my_dir + "/" + daily_wildcard)
    if not full_file_path:
        try_1 = [os.path.basename(x) for x in try_1]
    return [x for x in try_1 if re.search("[0-9]{8}\.txt$", x)]

def last_daily_of(my_dir = "c:/writing/daily", to_process = False, full_return_path = False):
    if to_process:
        my_dir = os.path.join(my_dir, "to-proc")
    if full_return_path:
        return os.path.normpath(os.path.join(my_dir, dailies_of(my_dir)[-1]))
    return dailies_of()[-1]

def github_root_of(my_path = os.getcwd()):
    ary = pathlib.PurePath(my_path).parts
    try:
        github_index = ary.index('github')
    except:
        return ''
    return os.path.join(pathlib.Path(*ary[:github_index+2]))

def progfile_of(my_path): # largely deprecated with most apps now being up to date
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

default_browser_exe = firefox_browser = firefox_string = progfile_of("c:\\Program Files\\Mozilla Firefox\\firefox.exe")
chrome_browser_exe = progfile_of("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
opera_browser_exe = "C:\\Users\\Andrew\\AppData\\Local\\Programs\\Opera\\opera.exe"
bing_browser_exe = bing_string = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

npnq = progfile_of("c:\\program files\\notepad++\\notepad++.exe")
np = '"{}"'.format(npnq)

def on_off(my_truth_state):
    return "on" if my_truth_state else "off"

def string_expand(my_string, my_expand_dictionary = mt_default_dict, force_lower = True):
    if '$' not in my_string:
        return my_string
    full_join = "|".join(my_expand_dictionary)
    join_string = r"\${{({})}}".format(full_join)
    if force_lower:
        join_string = join_string.lower()
    new_string = re.sub(join_string, lambda x: my_expand_dictionary[x.group(1)] if x.group(1) in my_expand_dictionary else "!!", my_string)
    return new_string

def truth_state_of(text_data, print_warning = True):
    tl = text_data.lower().strip()
    if tl == 'true' or tl == '1' or tl == 'yes': return True
    if tl == 'false' or tl == '0' or tl == 'no': return False
    if print_warning:
        print("Bad truth state:", text_data)
    return -1

def bail_if_not(f, file_desc = ""):
    if not os.path.exists(f): sys.exit("Need {:s}{:s}file {:s}".format(file_desc, " " if file_desc else "", f))

def filelines_no_comments(file_stream):
    return [ x for x in file_stream.readlines() if x.strip() and not x.startswith('#') and not x.startswith(";") ]

def errwrite(main_text, color = '', show_cr = True):
    if color:
        sys.stderr.write(color)
    sys.stderr.write(main_text)
    if color:
        sys.stderr.write(WTXT)
    if show_cr:
        sys.stderr.write('\n')

ew = errwrite

def warn(*txt):
    a = list(txt)
    a[0] = WARN + str(a[0])
    a[-1] = str(a[-1]) + WTXT
    print(*a)

def warnbail(*txt):
    warn(*txt)
    sys.exit()

bailwarn = warnbail

def fail(*txt):
    a = list(txt)
    a[0] = FAIL + str(a[0])
    a[-1] = str(a[-1]) + WTXT
    print(*a)

def failbail(*txt):
    fail(*txt)
    sys.exit()

bailfail = failbail

def okay(*txt):
    a = list(txt)
    a[0] = PASS + str(a[0])
    a[-1] = str(a[-1]) + WTXT
    print(*a)

def okaybail(*txt):
    okay(*txt)
    sys.exit()

passbail = bailpass = bailokay = okaybail

def cyan(*txt):
    a = list(txt)
    a[0] = PASS + str(a[0])
    a[-1] = str(a[-1]) + WTXT
    print(*a)

def cyanbail(*txt):
    okay(*txt)
    sys.exit()

bailcyan = cyanbail

def check_for_admin(bail = True):
    if sys.platform.startswith('win'):
        from win32com.shell import shell
        if not shell.IsUserAnAdmin():
            mt.warn("Need admin privileges!")
            if bail:
                sys.exit()

def emergency_file_of(my_file, time_format = "HH-mm-ss"):
    emer = "c:/writing/emergency"
    bn = os.path.basename(my_file)
    if not time_format:
        return os.path.normpath(os.path.join(emer, bn))
    add_time = pendulum.now().format(time_format)
    ary = bn.split('.')
    ary[0] += '-as-of-' + add_time
    return os.path.normpath(os.path.join(emer, '.'.join(ary)))

def is_alpha_match_special(my_string):
    return '>' in my_string or '<' in my_string or '|' in my_string

def alpha_match(var1, var2, case_insensitive = True, ignore_comments = True):
    if is_alpha_match_special(var2):
        if is_alpha_match_special(var1):
            print(colorama.Fore.YELLOW + "WARNING: ALPHA_MATCH TRIES TO COMPARE TWO CHARACTERS WITH WILD CARDS" + WTXT)
            return False
        return alpha_match(var2, var1, case_insensitive = case_insensitive)
    if case_insensitive:
        var1 = var1.lower()
        var2 = var2.lower()
    if ignore_comments:
        var1 = re.sub("#.*", "", var1).strip()
        var2 = re.sub("#.*", "", var2).strip()
    if '|' in var1:
        a = var1.index('|')
        left_side = sorted(var1[:a]) == sorted(var2[:a])
        right_side = sorted(var1[a+1:]) == sorted(var2[a:])
    elif '<' in var1:
        a = var1.index('<')
        left_side = sorted(var1[:a]) == sorted(var2[:a])
        right_side = var1[a+1:] == var2[a:]
    elif '>' in var1:
        a = var1.index('>')
        left_side = var1[:a] == var2[:a]
        right_side = sorted(var1[a+1:]) == sorted(var2[a:])
    else:
        return sorted(var1) == sorted(var2)
    return left_side and right_side

alf_match = alfmatch = alphamatch = alpha_match

def plur(a, choices=['s', '']):
    if type(choices) == str:
        choices = re.split('[/,]', choices)
        if len(choices) != 2:
            print("You need a CSV/slashed string if defining choices, and the length must be 2. Defaulting to s/(nothing).")
            choices = [ 's', '' ]
    if type(a) == str and a.isdigit():
        a = int(a)
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

def end_number_of(x):
    match_list = re.match('.*?([0-9]+)$', x)
    if not match_list:
        return 0
    print("end_number_of deprecated, use parameter_with_number instead")
    return int(match_list.group(1))

def is_basename(a):
    return not ('/' in a or '\\' in a)

def is_daily(x):
    if '/' in x or '\\' in x:
        x = os.path.basename(x).lower()
    return re.search("^2[0-9]{7}\.txt$", x)

is_daily_file = is_daily

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

def file_to_url(file_name):
    if file_name.startswith("file:/"):
        return file_name
    x = os.path.abspath(file_name)
    return "file:///" + x.replace('\\', '/')

def url_to_file(file_name):
    if not file_name.startswith("file:/"):
        return file_name
    x = re.sub("^file:[/]+", "", file_name)
    return os.path.normpath(x)

def num_value_from_text(my_line, my_index = 0):
    nums = re.findall("[0-9]+", my_line)
    try:
        return int(nums[my_index])
    except:
        return 0

def list_nums(my_list, separator=', '):
    return separator.join([str(x) for x in my_list])

num_list = nums_list = listnums = listnum = list_nums

# main usage (arg, num, value_found) = parnum(sys.argv[count]) returns string/number tuple
# see if we want to include a string instead of, say, a chopped off 1a2b3c

def parameter_with_number(x, also_lower = True, default_value = 0, allow_float = False, include_numbers_in_main_parameter = True):
    if x[0] == '-': x = x[1:]
    if also_lower:
        x = x.lower()
    digit_offset = re.search(r"\d", x)
    if not digit_offset:
        return (x, default_value, False)
    letters = x[:digit_offset.start()]
    numbers = x[digit_offset.start():]
    try:
        return (letters, int(numbers), True)
    except:
        pass
    try:
        temp = float(numbers)
        if not allow_float:
            print("WARNING allow_float must be set to allow floats")
            return (letters, default_value)
        return (letters, temp, True)
    except:
        pass
    return (x if include_numbers_in_main_parameter else letters, default_value, False)

num_let = numlet = letnum = let_num = numbers_letters = parnum = par_num = parameter_with_number

def nohy(x, also_lower = True): # mostly for command line argument usage, so -s is -S is s is S.
    if x[0] == '-': x = x[1:]
    if also_lower:
        return x.lower()
    return x

nohyp = noh = nohy

def decimal_only(val, digits = 3):
    fmt = "%.{}f".format(digits)
    ret = fmt % val
    if ret.startswith("0."):
        return ret[1:]
    if ret.startswith("-0."):
        return "-" + ret[2:]
    return ret

def is_open_in_notepad(my_file):
    my_norm = os.path.realpath(my_file)
    my_base = os.path.basename(my_norm)
    e = ET.parse(np_xml)
    for elem in e.iter('File'):
        this_np_file = elem.get("filename")
        if my_base.lower() not in this_np_file.lower(): continue # this speeds stuff up slightly
        if os.path.samefile(my_norm, this_np_file):
            return True
    return False

def modified_size_of(my_file):
    e = ET.parse(np_xml)
    quick_basename = os.path.basename(my_file).lower()
    for elem in e.iter('File'):
        this_np_file = elem.get("filename")
        if not os.path.exists(this_np_file): continue
        if quick_basename not in this_np_file.lower(): continue # this speeds stuff up slightly
        if os.path.samefile(this_np_file, os.path.abspath(my_file)):
            mso = elem.get("backupFilePath")
            if mso and os.path.exists(mso):
                return os.stat(mso).st_size
            else:
                break
    return os.stat(my_file).st_size

def is_npp_modified(my_file): # see if a file is unsaved in notepad++
    quick_basename = os.path.basename(my_file).lower()
    parse_successful = False
    while not parse_successful:
        try:
            e = ET.parse(np_xml)
            parse_successful = True
        except:
            messageBox = ctypes.windll.user32.MessageBoxW
            messageBox(None, "Error reading Notepad++ tabs.\n\nYou may need to wait to try again, especially if you just edited something.", "Try again!", 0x0)
    for elem in e.iter('File'):
        this_np_file = elem.get("filename")
        if quick_basename not in this_np_file.lower(): continue # this speeds stuff up slightly
        if os.path.samefile(this_np_file, os.path.abspath(my_file)):
            bfp = elem.get("backupFilePath")
            if bfp:
                if os.path.exists(bfp):
                    return True
            return False

def wait_until_npp_saved(my_file, bail = True):
    while is_npp_modified(my_file):
        messageBox = ctypes.windll.user32.MessageBoxW
        x = messageBox(None, "Save {} and hit OK and try again to open it in Notepad++.\n\nCANCEL aborts things.".format(my_file), "Try again!", 0x1)
        if x == 2: # Cancel ... OK is 1
            print("Okay, cancelling{}.".format(' and bailing' if bail else ''))
            if bail:
                sys.exit()
            return False
        elif x == 1:
            npo(my_file, bail = False)
    return True

def conditional_notepad_open_my_file(my_file, open_if_already_there):
    e = ET.parse(np_xml)
    already_in_notepad = is_open_in_notepad(my_file)
    n_t = "" if already_in_notepad else "n't"
    print("Conditionally opening", my_file, "in notepad. Open if it is{} available.".format(n_t))
    should_i_open = already_in_notepad != open_if_already_there
    print("{} because {} is{}".format("Opening" if should_i_open else "Skipping", my_file, n_t), "already open in notepad")
    if should_i_open:
        npo(my_file)
    else:
        return
    print("ERROR couldn't find", my_file)

def is_anagram(x, accept_comments = True, check_sections = True, wipe_author = True, ignore_leading_articles = True, wipe_inform_comments = True, need_all_sections = True):
    article_string = r'^(a|an|the) '
    if ignore_leading_articles and re.search(article_string, x):
        if is_anagram(re.sub(article_string, "", x, re.IGNORECASE), accept_comments, check_sections, wipe_author, ignore_leading_articles):
            return True
    x = re.sub("#.*", "", x)
    if wipe_author: # for book titles for Roiling
        x = re.sub("\[r\], +by +", "", x, re.IGNORECASE)
    if wipe_inform_comments: # for book titles for Roiling
        x = re.sub("\[.*?\]", "", x)
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
        if need_all_sections:
            if this_chunk != first_chunk:
                return False
        elif this_chunk == first_chunk:
            return True
    return True

is_anagramy = is_anagrammy = is_anagram

def is_limerick(x, accept_comments = False): # quick and dirty limerick checker
    if accept_comments and '#lim' in x: return True
    if x.count('/') != 4: return False
    temp = re.sub(".* #", "", x)
    if len(x) > 120 and len(x) < 240: return True

is_limericky = is_limerick

def is_palindrome(x, accept_comments = True, fail_on_unusual = True, decipher_asterisks = True):
    if accept_comments and "#pal" in x: return True
    if accept_comments: x = re.sub('#.*', '', x)
    if fail_on_unusual:
        if '=' in x or '~' in x:
            return False
    let_only = re.sub("[^a-z\*]", "", x.lower())
    if '*' in x:
        if decipher_asterisks:
            z = list(let_only)
            for y in range(0, len(z)):
                if z[y] == '*':
                    z[y] = z[len(z)-y-1]
            let_only = ''.join(z)
        else:
            let_only = let_only.replace('*', '')
    if not let_only: return False # blank strings don't work
    return let_only == let_only[::-1]

is_palindromey = is_palindromy = is_palindrome

def print_centralized(my_string, eliminate_control_chars = True):
    try: # needed if we pipe something
        x = os.get_terminal_size()
        screen_columns = x.columns
    except:
        screen_columns = 200
    length_string = my_string
    search_string = chr(0x1b) + "\[[0-9]+m"
    if eliminate_control_chars:
        length_string = re.sub(search_string, "", my_string)
    if len(length_string) > screen_columns:
        padding = 0
    else:
        padding = (screen_columns - len(length_string)) // 2
    print(' ' * padding + my_string)

center = centralized = print_center = print_centralized

def green_of(my_string, make_green = True):
    if not make_green:
        return my_string
    return colorama.Fore.GREEN + my_string + WTXT

def print_colored_centralized(my_string, color_string = colorama.Fore.GREEN, eliminate_control_chars = True):
    print_centralized(color_string + my_string + colorama.Back.BLACK + WTXT, eliminate_control_chars)

colcent = centcol = print_colored_centralized

def eq_print(my_text, equals_width = 20, centering = True, spacing = 1, color_info = ''):
    final_text = color_info + '=' * equals_width + ' ' * spacing + my_text + ' ' * spacing + '=' * equals_width + (WTXT if color_info else '')
    print_centralized(final_text)

def green_red_comp(num_to_be_greater, num_to_be_lesser, yellow_on_equals = True):
    if num_to_be_greater > num_to_be_lesser:
        return colorama.Fore.GREEN
    elif yellow_on_equals and num_to_be_lesser == num_to_be_greater:
        return colorama.Fore.YELLOW
    else:
        return colorama.Fore.RED

green_red = green_red_comp

def print_and_to_clip(my_str): # deprecated by how I can just use | CLIP but still useful if I only want 1-2 strings from the file
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

def change_cfg_line(file_name, var_to_change, new_value, delimiter = '=', report_error = True, print_success = False, allow_adding_line = False):
    var_to_change = var_to_change.lower()
    out_file = "c:/writing/temp/mytools_cfg_changed.txt"
    out_string = ""
    got_line = False
    new_line = "{}{}{}\n".format(var_to_change, delimiter, new_value)
    with open(file_name) as file:
        for (line_count, line) in enumerate (file, 1):
            if re.search(r"^{}\b".format(var_to_change), line):
                old_value = re.sub(r"^[^\b]*?", "", line.rstrip())
                if print_success:
                    print("Changing line", line_count, var_to_change, "from", old_value)
                got_line = True
                line = new_line
            out_string += line
    if not got_line:
        if allow_adding_line:
            if not out_string.endswith(new_line):
                out_string += "\n"
            out_string += new_line
            print("Tacked on the new data to line's end. Be sure to check to make sure it is reachable by the CFG reader.")
        else:
            print(colorama.Fore.RED + "WARNING attempt to change {} failed as no such line was in {}. Insert a line {}{} manually.".format(var_to_change, file_name, var_to_change, delimiter) + WTXT)
            return
    f = open(out_file, "w")
    f.write(out_string)
    f.close()
    if cmp(out_file, file_name, shallow=False):
        print(colorama.Fore.YELLOW + "WARNING nothing changed in {} even though we found a line starting with {}--variable was already set to {}.".format(file_name, var_to_change, new_value) + WTXT)
        return
    elif print_success:
        print(colorama.Fore.GREEN + "Changes seen between {} and {}. Copying.".format(out_file, file_name) + WTXT)
    try:
        copy(out_file, file_name)
    except:
        print("Could not copy temp-file back.")
        return
    try:
        os.remove(out_file)
    except:
        print(colorama.Fore.YELLOW + "MYTOOLS change_cfg_line failed to delete temp-cfg-rewrite output file {}. No big deal, as it'll be overwritten anyway. Just a warning.".format(out_file) + WTXT)
    if print_success:
        print("Successfully updated", file_name, "option", var_to_change, "to", new_value)
    return

def cfgary(x, delimiter="\t"): # A:b,c,d -> [b, c, d] # deprecated for cfg_data_split below
    if ':' not in x:
        print("WARNING, cfgary called on line without starting colon")
        return []
    temp = re.sub("^[^:]*:", "", x)
    return temp.split(delimiter)

# main usage (prefix, data) = cfg_data_split(line)
def cfg_data_split(x, delimiter=":=", to_tuple = True, strip_data_right_only = False, strip_line = True, dash_to_underscore = KEEP_DASH_UNDERSCORE, array_splitter = '', blank_second = False, lowercase_prefix = True, lowercase_data = True):
    if strip_line:
        x = x.strip()
    if dash_to_underscore == DASH_TO_UNDERSCORE:
        x = x.replace("-", "_")
    if dash_to_underscore == UNDERSCORE_TO_DASH:
        x = x.replace("_", "-")
    ary = re.split("[{}]".format(delimiter), x, 1)
    if lowercase_prefix:
        ary[0] = ary[0].lower()
    if lowercase_data:
        for x in range(1, len(ary)):
            ary[x] = ary[x].lower()
    if len(ary) == 1:
        if blank_second:
            return (ary[0], '')
        else:
            return ('', ary[0])
    if strip_data_right_only:
        ary[1] = ary[1].rstrip()
    elif strip_line:
        ary[1] = ary[1].strip()
    if to_tuple:
        return (ary[0], ary[1].split(array_splitter) if array_splitter else ary[1])
    return ary # (prefix, data) = general usage in programs

cfg_split = cfg_to_data = data_cfg_split = split_cfg_data = cfg_split_data = cfg_data_split

def quick_dict_from_line(my_line, init_separator=':', outer_separator = ',', inner_separator = '=', use_ints = False, use_floats = False, delete_before_colon = True, need_init_delimiter = True):
    my_line = my_line.strip()
    if need_init_delimiter and init_separator not in my_line:
        print("WARNING no colon in line", my_line, "so skipping, since we specified we need it.")
        return
    if delete_before_colon:
        if init_separator not in my_line:
            print("WARNING no initial separator {} in line <<{}>> but still processing.".format(init_separator, my_line))
        my_line = re.sub("^.*?" + init_separator, "", my_line)
    if use_floats:
        temp_dict = defaultdict(float)
    elif use_ints:
        temp_dict = defaultdict(int)
    else:
        temp_dict = defaultdict(str)
    if not my_line.count(outer_separator) or not my_line.count(inner_separator):
        return temp_dict
    ary = my_line.split(outer_separator)
    for x in ary:
        y = x.split(inner_separator)
        if len(y) != 2:
            print("Bad inner separator", my_line,x)
            continue
        if use_floats:
            temp_dict[y[0]] = float(y[1])
        elif use_ints:
            temp_dict[y[0]] = int(y[1])
        else:
            temp_dict[y[0]] = y[1]
    return temp_dict

def prefix_div(my_arg, delimiters = ":="):
    r = re.compile(r'[{}]'.format(delimiters))
    if not r.search(my_arg):
        return ('', my_arg)
    return r.split(my_arg, 1)

def text_from_values(my_dict, my_num):
    descending = sorted(my_dict, key=my_dict.get, reverse = True)
    for q in sorted(my_dict, key=my_dict.get, reverse = True):
        if my_num > my_dict[q]:
            return q
    try:
        return descending[-1]
    except:
        return 'black'

def check_properly_sectioned(my_file, allow_header = True, open_first_error = True, show_all_errors = True, report_success = True):
    in_section = False
    found_errors = False
    ever_section = False
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"): continue
            if not line.strip():
                in_section = False
                continue
            if line.startswith("\\"):
                if in_section:
                    print("Bad double-section at line {}.".format(line_count))
                    if open_first_error:
                        add_postopen(my_file, line_count)
                        if not show_all_errors:
                            postopen()
                    found_errors += 1
                in_section = True
                ever_section = True
            else:
                if not in_section:
                    if ever_section or not allow_header:
                        print("Line without section at line {}.".format(line_count))
                        if open_first_error:
                            add_postopen(my_file, line_count)
                            if not show_all_errors:
                                postopen()
                        found_errors += 1
    if open_first_error:
        postopen()
    if report_success:
        print("{} is properly sectioned.".format(my_file))
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

def lines_of(file_name, read_blanks = True):
    f = open(file_name, "r")
    temp = f.readlines()
    f.close()
    if not read_blanks:
        temp = [x for x in lines_of if x.strip()]
    return temp

def line_count_of(file_name, read_blanks = True):
    return len(lines_of(file_name, read_blanks = read_blanks))

HOST_MATCH_PERFECT = 1
HOST_MATCH_IGNORE_WWW = 1>>1
HOST_MATCH_SUBSITE = 1>>2

def web_site_match(site1, site2, match_type = HOST_MATCH_IGNORE_WWW):
    site1 = site1.lower()
    site2 = site2.lower()
    if site1 == site2:
        return True
    if match_type == HOST_MATCH_PERFECT:
        return False
    if match_type == HOST_MATCH_IGNORE_WWW:
        if site1 == 'www.' + site2:
            return True
        if site2 == 'www.' + site1:
            return True
    if match_type == HOST_MATCH_SUBSITE:
        if site2 in site1 or site1 in site2:
            return True
    return False

HOSTS_NOCHANGE = 0
HOSTS_UNREADABLE = 1>>1
HOSTS_UNWRITEABLE = 1>>2
HOSTS_RESTRICT = 1>>3
HOSTS_OPEN = 1>>4
HOSTS_UNKNOWN = 1>>5
HOSTS_FOUND_NOCHANGE = 1>>6

def hosts_file_toggle(my_website, allow_website_access, warn_no_changes = True, match_type = HOST_MATCH_IGNORE_WWW, set_read_after = False, auto_bail = False, look_for_start = True):
    my_website = my_website.lower()
    tracked_change = HOSTS_NOCHANGE
    the_temp_string = ""
    any_changes = False
    try:
        file = open(hosts_file)
    except:
        print("Could not open hosts file.")
        if auto_bail:
            sys.exit()
        return HOSTS_UNREADABLE
    skip_the_rest = False
    process_host_mappings = not look_for_start
    next_cr_go = False
    with file:
        for (line_count, line) in enumerate(file, 1):
            if next_cr_go and not line.strip():
                process_host_mappings = True
                next_cr_go = False
            if not process_host_mappings:
                if line.startswith('#') and 'localhost' in line:
                    next_cr_go = True
            if skip_the_rest:
                the_temp_string += line
                continue
            if "inserted by spybot" in line.lower():
                skip_the_rest = True
            x = re.split("[\t ]", line.strip().lower())
            if process_host_mappings and len(x) > 1 and web_site_match(x[1], my_website, match_type):
                temp = re.sub("^#+", "", x[0])
                if allow_website_access:
                    temp = '#' + temp
                if x[0] != temp:
                    if '#' in temp and '#' not in x[0]:
                        tracked_change |= HOSTS_RESTRICT
                    elif '#' in x[0] and '#' not in temp:
                        tracked_change |= HOSTS_OPEN
                    else:
                        tracked_change |= HOSTS_UNKNOWN
                    x[0] = temp
                    any_changes = True
                    the_temp_string += '\t'.join(x) + '\n'
                    continue
                else:
                    tracked_change |= HOSTS_FOUND_NOCHANGE
            the_temp_string += line
    if not process_host_mappings:
        print("Did not find LOCALHOST in file, and look_for_start was true, so I found nothing.")
        return
    if any_changes:
        try:
            os.chmod(hosts_file, stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH)
        except:
            print("I wanted to change the host file, but I could not properly open it for writing.\nMake sure you have administrative privileges with your script/function.")
            if auto_bail:
                sys.exit()
            return tracked_change | HOSTS_UNWRITEABLE
        f = open(hosts_file, "w")
        f.write(the_temp_string)
        f.close()
    elif warn_no_changes:
        if tracked_change & HOSTS_FOUND_NOCHANGE:
            print("WARNING: no websites matching {} were found in hosts_file_toggle.".format(my_website))
        else:
            print("WARNING: websites matching {} were found in hosts_file_toggle, but they were already set as requested.".format(my_website))
    if set_read_after:
        os.chmod(hosts_file, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    return tracked_change

def first_string_diff(string_1, string_2):
    min_length = min(len(string_1), len(string_2))
    for x in range(0, min_length):
        if string_1[x] != string_2[x]:
            return x
    if string_1 != string_2:
        return min_length
    return -1

def compare_alphabetized_lines(f1, f2, bail = False, max = 0, ignore_blanks = False, verbose = True, max_chars = 0, mention_blanks = True, red_regexp = '', green_regexp = '', show_bytes = False, verify_alphabetized_true = True, compare_tabbed = False, sections_to_ignore = [], case_insensitive = False): # returns true if identical (option to get rid of blanks,) false if not
    if verbose:
        print("Comparing alphabetized lines: {} vs {}.".format(f1, f2))
    if f1 == f2:
        print("You are comparing {} to itself.".format(f1))
        return True
    freq = defaultdict(int)
    total = defaultdict(int)
    f1_ary = lines_of(f1)
    f2_ary = lines_of(f2)
    if case_insensitive:
        f1_ary = [x.lower() for x in f1_ary]
        f2_ary = [x.lower() for x in f2_ary]
    ignore_stuff = False
    for line in f1_ary:
        for q in sections_to_ignore:
            if line.startswith(q):
                ignore_stuff = True
        if not line.strip():
            ignore_stuff = False
        if ignore_stuff:
            continue
        freq[line.lower().strip()] += 1
        total[line.lower().strip()] += 1
    for line in f2_ary:
        for q in sections_to_ignore:
            if line.startswith(q):
                ignore_stuff = True
        if not line.strip():
            ignore_stuff = False
        if ignore_stuff:
            continue
        freq[line.lower().strip()] -= 1
        total[line.lower().strip()] += 1
    difs = [x for x in freq if freq[x]]
    if ignore_blanks and '' in difs: difs.remove('')
    left = 0
    right = 0
    totals = 0
    bn1 = os.path.basename(f1)
    bn2 = os.path.basename(f2)
    space_delta = len(bn1) - len(bn2)
    if bn1 == bn2:
        bn1 = f1
        bn2 = f2
    any_extra_lines = False
    if compare_tabbed:
        tabbed_entries = [x for x in freq if '\t' in x and x.strip()]
        if len(tabbed_entries) == 0:
            pass
        elif len(tabbed_entries) != 1:
            print("WARNING found more than one tabbed line when comparing tabs:")
            if tabbed_entries[0] in f2_ary:
                (tabbed_entries[0], tabbed_entries[1]) = (tabbed_entries[1], tabbed_entries[0])
            difs = [x for x in difs if '\t' not in x]
            tabs1 = tabbed_entries[0].split("\t")
            tabs2 = tabbed_entries[1].split("\t")
            set1 = set(tabs1) - set(tabs2)
            set2 = set(tabs2) - set(tabs1)
            if (set1 or set2):
                print_centralized(colorama.Fore.YELLOW + "TAB STRING DIFFERENCE" + WTXT)
            if set1:
                fail("    ORIG:", ', '.join(['{} idx {}'.format(x, tabbed_entries[0].index(x) + 1) for x in set1]))
            if set2:
                okay("     NEW:", ', '.join(['{} idx {}'.format(x, tabbed_entries[1].index(x) + 1) for x in set2]))
            if '' in set1 or '' in set2:
                warn("Search for \\t\\t or \\t$ if you need to weed out extraneous tabs.")
    if len(difs):
        for j in sorted(difs):
            if freq[j] > 0 : left += 1
            else: right += 1
            totals += 1
            if not max or totals <= max:
                j2 = j
                if max_chars and len(j) > abs(max_chars):
                    j2 = j[:max_chars] + " ..." if max_chars > 0 else "... " + j[max_chars:]
                if not mention_blanks and not j2:
                    continue
                if not any_extra_lines:
                    print("=" * 20 + " BEGIN DIFFERENCES " + "=" * 20)
                    any_extra_lines = True
                print_string = "{}{}{}".format(bn1 if freq[j] > 0 else ' ' * len(bn1), '<<<<' if freq[j] > 0 else '>>>>', bn2 if freq[j] < 0 else ' ' * len(bn2))
                print_string += " Extra Line {}".format("<blank>" if not j2 else j2)
                print_string += " / {:d} diff ({:d} vs {:d}) in {:s}".format(abs(freq[j]), (total[j]-abs(freq[j]))//2, (total[j]+abs(freq[j]))//2, bn1 if freq[j] > 0 else bn2) # different # of >>/<< to make eyeball comparisons (if necessary) easier
                color_flags = 0
                if red_regexp:
                    if re.search(red_regexp, j):
                        color_flags |= 1
                    elif not green_regexp:
                        color_flags |= 2
                if green_regexp:
                    if re.search(green_regexp, j):
                        color_flags |= 2
                    elif not green_regexp:
                        color_flags |= 1
                color_array = [ colorama.Fore.WHITE, colorama.Fore.RED, colorama.Fore.GREEN, colorama.Fore.YELLOW ]
                print_string = color_array[color_flags] + print_string + WTXT
                print(print_string)
            elif max and totals == max + 1:
                print("Went over maximum of", max)
        if any_extra_lines:
            print("=" * 21 + " END DIFFERENCES " + "=" * 21)
        print("{} has {} extra mismatches but {} has {}.".format(os.path.basename(f1), left, os.path.basename(f2), right))
        if show_bytes and len(difs):
            f1s = os.stat(f1).st_size
            f2s = os.stat(f2).st_size
            print("OLD: {} lines {} bytes, NEW: {} lines {} bytes, DELTA: {} lines {} bytes.".format(len(f1_ary), f1s, len(f2_ary), f2s, len(f2_ary) - len(f1_ary), f2s-f1s))
        if len(difs) == 1 and difs[0] == '':
            print("ONLY BLANKS are different. You can run this function with ignore_blanks = True.")
        if bail:
            print("Compare shuffled lines is bailing on difference.")
            sys.exit()
        return False
    elif verify_alphabetized_true:
        print_centralized(colorama.Back.GREEN + "THERE ARE NO DIFFERENCES BETWEEN ALPHABETIZED VERSIONS OF {} AND {}.".format(bn1, bn2) + WTXT)
    if verbose:
        print("No shuffle-diffs")
    return True

cs = ca = compare_shuffled_lines = cal = calf = compare_alphabetized_lines

def line_in_file(my_file, open_at_text, start_with = True):
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if start_with and line.startswith(open_at_text):
                return line_count
            elif open_at_text in line:
                return line_count
    print("Was unable to find the line", open_at_text, "in", my_file)
    return -1

def npo(my_file, my_line = -1, print_cmd = True, to_stderr = True, bail = True, follow_open_link = True, print_full_path = False, my_opt_bail_msg = '', open_at_text = ''):
    if to_stderr:
        old_stdout = sys.stdout
        sys.stdout = sys.stderr
    if not os.path.exists(my_file):
        print("WARNING:", my_file, "does not exist.")
    elif follow_open_link:
        my_file = os.path.realpath(my_file)
        if not os.path.exists(my_file):
            print("WARNING: linked-to file", my_file, "does not exist.")
    if os.path.exists(my_file):
        if open_at_text:
            my_line = line_in_file(my_file, open_at_text)
        line_to_open = "" if my_line == -1 else " -n{}".format(my_line)
        cmd = "start \"\" {:s} \"{:s}\"{}".format(np, my_file, line_to_open)
        if print_cmd: print("Launching {:s} {} in notepad++{:s}.".format(
            my_file if print_full_path else os.path.basename(my_file),
            'at the start' if my_line < 0 else "at line {}".format(my_line),
            " and bailing" if bail else ""))
        os.system(cmd)
    else:
        print("Unable to find", my_file)
    if bail:
        if my_opt_bail_msg != '':
            print(colorama.Fore.GREEN + my_opt_bail_msg + WTXT)
        sys.exit()
    if to_stderr:
        sys.stdout = old_stdout

open_in_notepad = notepad_open = npo

def open_this(bail = True):
    try:
        npo(main.__file__, bail=bail)
    except Exception as e:
        print("Could not open source", main.__file__)
        print("Error thrown:")
        print(e)
        if bail:
            sys.exit()

def add_postopen_file_line(file_name, file_line = 1, rewrite = False, reject_nonpositive_line = True, priority = 10, note_open_try = True):
    if file_line <= 0 and reject_nonpositive_line: return
    if type(file_name) != str:
        print(colorama.Fore.RED + "WARNING: YOU PROBABLY TRIED TO SEND A FILE STREAM TO ADD_POSTOPEN")
        for my_arg in traceback.format_stack()[:-1]:
            ary = my_arg.split("\n")
            any_yet = False
            for a in ary:
                if a:
                    print(("    " if any_yet else "----") + a)
                    any_yet = True
        print(WTXT, end='')
        return
    if file_name in file_post_list:
        try:
            file_extra_edit[file_name] += 1
        except:
            file_extra_edit[file_name] = 1
    if rewrite or file_name not in file_post_list or priority not in file_post_list[file_name]:
        file_post_list[file_name][priority] = file_line

add_open = add_post = add_postopen = add_post_open = addpost = add_postopen_file_line

NOTE_EMPTY = 1
BAIL_ON_EMPTY = 2

def postopen_files(bail_after = True, max_opens = 0, sleep_time = 0.1, show_unopened = True, full_file_paths = False, test_run = False, blank_message = "There weren't any files slated for opening/editing.", sort_type = SORT_ALPHA_NONE, sort_by_max_priority = False, min_priority = 0, empty_flags = 0, to_stderr = True, allow_first_as_extra = False):
    if to_stderr:
        old_stdout = sys.stdout
        sys.stdout = sys.stderr
    files_to_post = [x for x in file_post_list if max(file_post_list[x]) >= min_priority]
    if sort_type == SORT_ALPHA_FORWARD:
        files_to_post = sorted(files_to_post, key=lambda x:os.path.basename(x))
    elif sort_type == SORT_ALPHA_BACKWARD:
        files_to_post = sorted(files_to_post, key=lambda x:os.path.basename(x), reverse = True)
    if max_opens and allow_first_as_extra:
        a = files_to_post[0]
        amax = max(file_post_list[a])
        print(a, amax)
        this_max = max([max(file_post_list[x]) for x in files_to_post])
        if amax != this_max:
            file_post_list[a][this_max] = file_post_list[a][amax]
            max_opens += 1
    if sort_by_max_priority:
        files_to_post = sorted(files_to_post, key=lambda x:-max(file_post_list[x]))
    if len(file_post_list):
        got_yet = defaultdict(bool)
        l = len(files_to_post)
        count = 0
        for x in files_to_post:
            if max_opens and count == max_opens and l > max_opens:
                print("Reached max_opens of", max_opens, "so I am cutting it off here.")
                if show_unopened:
                    temp = [y for y in file_post_list if y not in got_yet]
                    print("Remaining file{}:".format(plur(len(temp))))
                    for y in file_post_list:
                        if y not in got_yet:
                            print("    ----{}".format(y))
                break
            got_yet[x] = True
            m = max(file_post_list[x])
            bnx = os.path.basename(x)
            if x in file_extra_edit:
                print("    {} additional suggested line-opening{} for {} {} ignored. If you're searching for errors, you may have to run things again.".format(file_extra_edit[x], plur(file_extra_edit[x]), bnx, plur(file_extra_edit[x], [ 'were', 'was' ])))
            el = len(file_post_list[x])
            if el > 1:
                print("Errors of {} different priorities were found in {}, so the first/last one may not be flagged. Just the most important one.".format(el, bnx))
            if test_run:
                print("Would've opened", x, "at line", file_post_list[x][m])
            else:
                npo(x, file_post_list[x][m], bail = False, print_full_path = full_file_paths, to_stderr = to_stderr)
            count += 1
            if count < len(file_post_list):
                time.sleep(sleep_time)
    else:
        if empty_flags & NOTE_EMPTY:
            print(blank_message)
        if empty_flags & BAIL_ON_EMPTY:
            sys.exit()
        else:
            return
    if bail_after and len(file_post_list):
        sys.exit()
    file_post_list.clear()
    if to_stderr:
        sys.stdout = old_stdout

post_open = postopen = openpost = open_post = postopen_files

def open_source(bail = True):
    npo(main.__file__)
    if bail: exit()

# can't use os as it is, well, an imported package
o_s = open_source

def open_source_config(bail = True):
    npo(re.sub("py$", "txt", main.__file__))
    if bail: exit()

oc = o_c = open_config = open_source_config

def create_temp_alf(file_1, file_2, comments, spaces, ignorable_strings=[]):
    l = sorted(open(file_1).readlines())
    f2 = open(file_2, "w")
    for x in l:
        if x.strip() not in ignorable_strings: continue
        if spaces == False and not x.strip(): continue
        if comments == False and x.startswith("#"): continue
        f2.write(x)
    f2.close()

def strip_punctuation(q, zap_bounding_apostrophe = False, other_chars_to_zap = '', lowercase_it = True, remove_comments = False, ignore_after = []):
    if remove_comments and '#' in q:
        q = zap_comment(q)
    for y in ignore_after:
        if y in q:
            q = re.sub(y + ".*", "", q)
    q = q.replace('"', '')
    if zap_bounding_apostrophe:
        q = re.sub("(\b'|'\b)", "", q)
    q = q.replace('.', '')
    q = q.replace(',', '')
    q = q.replace('-', ' ')
    q = q.replace('!', '')
    q = q.replace('?', '')
    q = q.replace('~', '')
    q = q.replace("[']", '') # inform 7 tweak
    q = q.replace("'", '')
    if '  ' in q:
        q = re.sub(" {2,}", " ", q)
    q = ' '.join(q.split(' '))
    q = re.sub("^(an|the|a) ", "", q).strip()
    for x in other_chars_to_zap:
        q = q.replace(x, '')
    if lowercase_it:
        q = q.lower()
    return q

def alphabetize_lines(x, ignore_punctuation_and_articles = True):
    if type(x) == str:
        temp = x.split("\n")
    return "\n".join(sorted(temp, key=lambda x:strip_punctuation(x) if ignore_punctuation_and_articles else x.lower())) + "\n"

def quote_spaced_file(my_file):
    if '"' in my_file:
        return my_file
    if ' ' in my_file:
        return '"' + my_file + '"'
    return my_file

def alfcomp(x1, x2, bail_on_show_winmerge = True, comments = True, spaces = False, show_winmerge = True, acknowledge_comparison = True, quiet = True, ignorable_strings=[]):
    a1 = "c:/writing/temp/alpha-1.txt"
    a2 = "c:/writing/temp/alpha-2.txt"
    if acknowledge_comparison and not quiet:
        print("Alphabetical comparison: {} vs {}".format(x1, x2))
    create_temp_alf(x1, a1, comments, spaces)
    create_temp_alf(x2, a2, comments, spaces)
    temp = cmp(a1, a2)
    if show_winmerge and not temp:
        wm(a1, a2)
        os.remove(a1)
        os.remove(a2)
        if bail_on_show_winmerge: sys.exit()
    return temp

def first_diff(x1, x2, one_based = True):
    f = open(x1, 'r')
    r1 = f.readlines()
    f.close()
    f = open(x2, 'r')
    r2 = f.readlines()
    f.close()
    ml = min(len(r1), len(r2))
    for x in range(0, ml):
        if r1[x] != r2[x]:
            return x
    if x == len(r2) and x == len(r1):
        return -1
    return len(r1)

def open_first_diff(x1, x2, bail = True):
    which_line = first_diff(x1, x2)
    if which_line > -1:
        npo(x1, which_line)
    print("No differences between {} and {}!".format(x1, x2))
    if bail:
        sys.exit()

def wm(x1, x2, ignore_if_identical = True, quiet = False):
    if ignore_if_identical and cmp(x1, x2):
        if not quiet:
            print("Not comparing identical files", x1, "and", x2, "in WinMerge.")
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

def last_mod(x, follow_links = True):
    if follow_links:
        return os.stat(os.path.abspath(x)).st_mtime
    else:
        return os.lstat(os.path.abspath(x)).st_mtime

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

def browser_or_native(file_name, print_action = True, bail = False, return_to_orig = True, open_in_web = True, my_browser = ''): # was text in browser but we can also view PNGs there
    is_url = file_name.startswith("http:") or file_name.startswith("https:")
    if not is_url:
        file_name = os.path.abspath(file_name)
    if not open_in_web:
        os.system(file_name)
    else:
        browser_path = default_browser_exe
        if my_browser == 'c' or my_browser == 'chrome':
            browser_path = chrome_browser_exe
        elif my_browser == 'f' or my_browser == 'firefox':
            browser_path = firefox_browser_exe
        elif my_browser == 'o' or my_browser == 'opera':
            browser_path = opera_browser_exe
        import win32gui
        #obsolete -- subprocess launches Firefox without hogging the command line
        # cmd = 'start \"\" \"{}\" \"file:///{}\"'.format(default_browser_exe, file_name)
        if print_action:
            print("Opening {} with {}.".format(file_name, browser_path))
        old_window = win32gui.GetForegroundWindow()
        subprocess.call([browser_path, file_name if is_url else pathlib.Path(file_name).as_uri()])
    if return_to_orig:
        time.sleep(.05) # for whatever reason, we need a fraction of a second before this comes back
        win32gui.SetForegroundWindow(old_window)
    if bail:
        sys.exit()

open_in_browser = file_in_browser = file_in_browser_conditional = gib = g_i_b = graphics_in_browser = tib = t_i_b = text_in_browser = fib = f_i_b = browser_or_native

def text_to_browser(my_text, delete_immediately = True, bail = False):
    file_name = os.path.join("c:/writing/temp", pendulum.now().format("YYYY-MM-DD-HH-mm-SS") + '.txt')
    f = open(file_name, "w")
    f.write(my_text)
    f.close()
    browser_or_native(file_name)
    if delete_immediately:
        time.sleep(.1)
        os.remove(file_name)
    if bail:
        sys.exit()

COMMENT_COMBINE_NONE = 0
COMMENT_COMBINE_CASE_SENSITIVE = 1
COMMENT_COMBINE_CASE_INSENSITIVE = 2

def comment_combine(my_lines, cr_at_end = True, conflate_duplicates = COMMENT_COMBINE_CASE_INSENSITIVE, to_flag = [], add_to_blank = 'noted more than once'):
    if type(cr_at_end) != bool and type(cr_at_end) != int:
        raise ValueError('You probably sent a couple strings instead of an array of strings: <<{} / {}>>'.format(my_lines, cr_at_end)) from None
    main_line_string = ""
    comment_array = []
    for x in my_lines:
        if not '#' in x:
            main_line_string += " " + x.strip()
            continue
        temp_ary = [y.strip() for y in x.strip().split("#", 1)]
        main_line_string += " " + temp_ary[0].strip()
        if temp_ary[1] in to_flag:
            print(WARN + "Weeded out {} from {}.".format(temp_ary[1], temp_ary[0]) + WTXT)
            continue
        comment_array.append(temp_ary[1].strip())
    if conflate_duplicates == COMMENT_COMBINE_NONE:
        final_array = comment_array
    else:
        final_array = []
        final_array_lower = []
        for c in comment_array:
            if c in final_array:
                continue
            if (conflate_duplicates == COMMENT_COMBINE_CASE_INSENSITIVE) and c.lower() in final_array_lower:
                continue
            final_array.append(c)
            final_array_lower.append(c.lower())
    if not len(final_array) and add_to_blank:
        final_array.append(add_to_blank)
    if len(final_array):
        main_line_string += " # " + " / ".join(final_array)
    if cr_at_end:
        main_line_string += "\n"
    return main_line_string.lstrip()

comcom = comment_combine

def zap_comment(my_line, zap_spaces_before = True, zap_brackets = True):
    temp = re.sub("#.*", "", my_line)
    if zap_spaces_before:
        temp = temp.strip()
    if zap_brackets:
        temp = re.sub("\[[^\]]*\]$", "", temp).rstrip()
    return temp

no_comment = no_comments = comment_zap = comments_zap = zapcomments = zapcomment = zap_comments = zap_comment

def is_comment_or_blank(my_line):
    return not zap_comment(my_line).strip()

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
                last_time = y.st_mtime
        except:
            print("No info for", x)
    if not new_ret: sys.exit("Can't get latest of {}".format(', '.join(file_array)))
    return new_ret

def proper_constraints(my_permutation, constraints_array):
    for c in constraints_array:
        if not c:
            continue
        if '!' in c:
            ary = c.split('!')
            ary2 = [ int[x] for x in c[1].split(',') ]
            if my_permutation.index(int(ary[0])) in ary2:
                return False
            continue
        if '@' in c:
            ary = c.split('@')
            ary2 = [ int[x] for x in c[1].split(',') ]
            if my_permutation.index(int(ary[0])) not in ary2:
                return False
            continue
        tries = [int(x) for x in re.split('[<>]', c)]
        first_smaller = my_permutation.index(tries[0]) < my_permutation.index(tries[1])
        if first_smaller != ('<' in c):
            return False
    return True

def first_timed_file_of(file_array, latest = True):
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

first_of = first_timed_file_of

def win_or_print(string_to_print, header_to_print, windows_popup_box, time_out = 0, bail = False, width = 400, height = 400):
    if type(string_to_print) == list:
        try:
            string_to_print = "\n".join(string_to_print)
        except:
            print("Bad string-to-print passed to win_or_print.")
            return
    if time_out:
        print("tkinter...")
        import tkinter as tk
        root = tk.Tk()
        root.geometry("{}x{}".format(width, height))
        root.title(header_to_print)
        tk.Label(root, text=string_to_print).pack()
        root.after(time_out * 1000, lambda: root.destroy())     # time in ms
        root.mainloop()
    elif windows_popup_box:
        messageBox = ctypes.windll.user32.MessageBoxW
        messageBox(None, string_to_print, header_to_print, 0x0)
    else:
        print(string_to_print)
    if bail:
        sys.exit()

def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

is_admin = admin = isadmin = Admin = isAdmin

def has_toproc_duplicate(file_name):
    file_full = os.path.realpath(file_name)
    q = os.path.split(file_full)
    q2 = os.path.join(q[0], 'to-proc', q[1])
    return os.path.exists(q2)

def follow_link(x):
    sys.stderr.write("WARNING: follow_link is deprecated in favor of os.path.realpath.")
    temp = x
    count = 0
    while os.path.islink(temp):
        if count == 11: sys.exit("Failed to resolve symlink: {}".format(temp))
        temp = os.readlink(temp)
        count += 1
    if temp.startswith("\\\\?\\"):
        temp = temp[4:]
    return temp

def section_of(my_file, my_section_name, absolute_name = False, return_line_count = True, return_header = True):
    got_section = False
    in_section = False
    section_string = ''
    start_line = 0
    if not my_section_name.startswith("\\"):
        my_section_name = "\\" + my_section_name
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if not in_section and line.startswith(my_section_name):
                if not absolute_name:
                    in_section = True
                    got_section = True
                    if not return_header:
                        continue
                else:
                    title = re.sub("=.*", "", line.strip())
                    if title == my_section_name:
                        start_line = line_count
                        in_section = True
                        got_section = True
                        if not return_header:
                            continue
            if in_section and not line.strip():
                in_section = False
            if in_section:
                section_string += line
    if not got_section:
        warn("WARNING: could not find section {} in {}.".format(my_section_name, my_file))
    if return_line_count:
        return (section_string, start_line)
    return section_string

my_section_of = section_of

def safemove(f1, f2, bail_on_fail = True):
    if os.path.exists(f2):
        warn("{} exists, not moving.".format(f2))
        if bail_on_fail:
            sys.exit()
    shutil.move(f1, f2)
    shutil.move(safe_temp)

def safeswap(f1, f2, bail_on_fail = True):
    safe_temp = "c:/writing/temp/mt-safe-temp"
    if os.path.exists(safe_temp):
        sys.exit("Being extra cautious. {} exists. Delete before continuing.".format(safe_temp))
    safemove(f1, safe_temp)
    safemove(f2, f1)
    safemove(safe_temp, f1)
    mt.okay("Successfully switched {} and {}.".format(f1, f2))

#####################################################basic main-program checking stuff

if os.path.basename(main.__file__) == "mytools.py":
    print("mytools.py is a header file. It should not be run on its own.")
    print("Try running something else with the line import i7, instead, or ? to run a test.")
    sys.exit()
