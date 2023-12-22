# nitxt.py
#
# originally just extacted game text between quotes but now can get game text size in words or misspelled words
#
# it does this for story.ni as well as the non-common files in the header
#
# usage: optional file name (e.g. for escape.xvn)
# -nr / -rn / -rb = toggles whether or not to rub what is between brackets, which overrides extension settings
#
# for STS nitxt.py -tests,random +sts
#
# todo: create file with forbidden words by project and create dicts of define default word lists
#

from collections import defaultdict
import i7
import os
import sys
import codecs
import re
import mytools as mt

see_misspelled = False

tally = defaultdict(int)

good_files = [ 'story.ni', 'source_code.adv' ]

skip_single_words = False
errors_only = False

count = 0
total_words = 0

default_word_list = []

words_to_find = []
word_dict = defaultdict(int)
already_got = defaultdict(bool)

rub_brackets = True

include_files = []
ignores = []
accepts = []

forbidden_words = []
forbidden_lines = []

my_name = "Andrew Schultz"
my_dir = "c:/program files (x86)/inform 7/inform7/Extensions/Andrew Schultz"

def usage(header = 'main usage'):
    print('=' * 20, header, '=' * 20)
    print("Main usage is nitxt.py f=(forbidden word)")
    print("Usage for STS is nitxt.py -tests,random +sts")
    print("c= / cd checks with a text file. The default forbidden word list is", default_word_list)
    sys.exit()

def ext_2_brax(file_name):
    if file_name.endswith('xvn'): return False # Marnix Van Den Bos's XVAN system. For the sample game Escape.
    if file_name.endswith('ni'): return True
    return False

def which_of():
    for x in good_files:
        if os.path.exists(x):
            return x
    sys.exit("Could not find a valid source file.")

def count_misspelled(my_dict):
    word_dict = defaultdict(int)
    with open(mt.words_file) as file:
        for (line_count, line) in enumerate (file, 1):
            l = line.strip().lower()
            word_dict[l] = 1
    for m in my_dict:
        if m not in word_dict:
            print(m, "not in dictionary, seen {} times.".format(my_dict[m]))

def file_read_clipboard(my_file):
    the_array = []
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#"):
                continue
            if line.startswith(";"):
                continue
            the_array += line.strip().split(',')
    return the_array

def find_words(this_file, this_dict):
    fb = os.path.basename(this_file)
    with open(this_file) as file:
        for (line_count, line) in enumerate (file, 1):
            quoted_line = ' '.join(line.split('"')[1::2])
            stuff_after = []
            for x in this_dict:
                if this_dict[x] >= 5:
                    continue
                if x in line and re.search(r"\b{}\b".format(x), quoted_line):
                    this_dict[x] += 1
                    stuff_after.append(x)
            if len(stuff_after):
                    print("{:30} {:5d} {}".format(fb, line_count, ', '.join(stuff_after)))
                    print("          " + line.strip())
    return this_dict

def get_text(file_name, get_include, only_get_include_files = False):
    global forbidden_lines
    if file_name in already_got:
        print(("=" * 30) + "Already got", file_name)
        return
    already_got[file_name] = True
    print(("=" * 60) + "Looking at", file_name)
    global include_files
    this_table = ''
    fb = os.path.basename(file_name)
    rough_word_count = 0
    with codecs.open(file_name, "r", "utf-8") as file:
    # with open(file_name) as file:
        cur_line = ""
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("understand") and "mistake" not in line:
                continue
            if line.startswith("test ") and " with " in line:
                continue
            if line.startswith("table of") and "\t" not in line:
                this_table = re.sub("\[.*", "", line).strip()
            if not line.strip():
                this_table = ''
            if get_include and re.search("^include .* by andrew schultz", line, re.IGNORECASE):
                inclu = re.sub("Include +", "", line.strip(), 0, re.IGNORECASE)
                inclu = re.sub(" by %s.*" % my_name, "", inclu, 0, re.IGNORECASE)
                inclu = my_dir + "/" + inclu + ".i7x"
                if inclu in include_files:
                    print("Re-included", inclu)
                include_files.append(inclu)
                #print("Should also read", inclu)
            if only_get_include_files:
                continue
            if '  ' in line:
                lq = ''.join(line.split('"')[1::2])
                if '  ' in lq:
                    print("Double-space at line", line_count, "index", line.find("  "), line.strip())
            if line.rstrip().endswith("/"):
                # print("CONTINUANCE ENDS WITH /: line", line_count, line.rstrip())
                cur_line += line.strip()[:-1]
                continue
            if "\"" not in line and not cur_line:
                continue
            cur_line += line.strip()
            # print("Line", line_count, cur_line)
            x = cur_line.strip().split("\"")[1::2]
            for y in x:
                if skip_single_words:
                    if ' ' not in y and '-' not in y:
                        continue
                if rub_brackets: temp = re.sub("\[[^\]]+\]", " / ", y)
                else: temp = y
                temp = re.sub("\['\]", "'", temp)
                temp = re.sub(" +", " ", temp)
                temp = re.sub(r'\\n', " ", temp)
                if not errors_only:
                    if re.search("[A-Za-z]", temp):
                        print("Line {}{}: {}".format(line_count, ' ({})'.format(this_table) if print_tables and this_table else '', temp))
                if line_count == 1:
                    continue
                for f in forbidden_words:
                    if f.lower() in temp.lower():
                        forbidden_lines.append("Forbidden word {} present in {} at line {}: {}.\n".format(f, fb, line_count, y))
                if '  ' not in y:
                    rough_word_count += y.count(' ')
                word_array = re.split("[ /-]+", temp)
                for w in word_array:
                    if not w:
                        continue
                    w = re.sub("[^a-zA-Z]", "", w)
                    tally[w.lower()] += 1
            cur_line = ""
    print("Rough word count:", rough_word_count)
    return rough_word_count

count = 1
file_name = ""
rub_brackets_from_file = True
project_only = True
author_only = False
my_title = i7.dir2proj()
print_tables = True

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg.startswith('-'):
        ignores.extend(arg[1:].split(','))
    elif arg.startswith('+'):
        accepts.extend(arg[1:].split(','))
    elif arg == 'rb':
        rub_brackets = True
        rub_brackets_from_file = False
    elif arg == 'nr' or arg == 'rn':
        rub_brackets = False
        rub_brackets_from_file = False
    elif arg == 'o':
        project_only = True
    elif arg in ( 'on', 'no' ):
        project_only = False
    elif arg in ( 'pt', 'tp' ):
        print_tables = True
    elif mt.alfmatch(arg, 'npt'):
        print_tables = False
    elif arg == 'a':
        author_only = True
    elif arg == 'eo':
        errors_only = True
    elif arg == 'ms':
        see_misspelled = True
    elif arg[:2] == 'cd':
        words_to_find = default_word_list
    elif arg[:2] == 'c=':
        words_to_find = file_read_clipboard(arg[2:])
    elif arg == 'cl':
        words_to_find = pyperclip.paste().split("\n")
    elif arg[:2] == 'n=':
        author_name = arg[2:]
    elif arg == 'ss':
        skip_single_words = True
    elif arg[:2] in ( 'w=', 'f=' ):
        forbidden_words.extend(arg[2:].split(','))
    else:
        if '.' in arg:
            if file_name: sys.exit("Tried to define 2 file names or had a bad flag.")
            file_name = arg
        else:
            usage('Bad argument {}'.format(arg))
    count += 1

if not file_name:
    file_name = which_of()

if rub_brackets_from_file:
    rub_brackets = ext_2_brax(file_name)

if len(words_to_find):
    for x in words_to_find:
        word_dict[x] = 0
    word_dict = find_words(file_name, word_dict)
    total_words += get_text(file_name, True, only_get_include_files = True)
else:
    total_words += get_text(file_name, True)

for x in include_files:
    xb = os.path.basename(x)
    if author_only and my_name.lower() not in x.lower():
        print("Skipping not-by-author", xb)
        continue
    if project_only and my_title.lower().replace('-', ' ') not in x.lower() and my_title.lower().replace('-', '') not in x.lower():
        force_accept = False
        for a in accepts:
            if a in x.lower():
                force_accept = True
        if not force_accept:
            print("Skipping non-specific header", xb, "as it is missing", my_title)
            continue
    ignore_skip = False
    for i in ignores:
        if i in x.lower():
            print("Skipping {} since ignorable string {} is in it.".format(x, i))
            ignore_skip = True
    if ignore_skip:
        continue
    if len(words_to_find):
        word_dict = find_words(x, word_dict)
    else:
        total_words += get_text(x, False)

if len(words_to_find):
    maxes = [x for x in word_dict if word_dict[x] >= 5]
    nones = [x for x in word_dict if word_dict[x] == 0]
    print("At the maximum:", maxes)
    print("No matches:", nones)

if len(forbidden_words):
    if len(forbidden_lines):
        print("Forbidden words found:", len(forbidden_lines))
        for x in forbidden_lines:
            sys.stderr.write(x)
    else:
        print("Forbidden words were all redacted!")

print("Total rough word count:", total_words)

if see_misspelled:
    count_misspelled(tally)
else:
    print("ms flag sees what words are misspelled, as a small bonus.")
