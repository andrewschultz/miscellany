#
# punc.py
#
# replaces punc.pl
#
# usage: so far only projects on the command line
#

import i7
import re
import sys
import os

from filecmp import cmp
from collections import defaultdict
import mytools
from mytools import title_words

cur_proj = ""
default_proj = ""

temp_table_file = "c:/writing/temp/punc-temp.i7x"

title_words_to_ignore = defaultdict(bool)
ignores = defaultdict(list)
file_list = defaultdict(list)
rubrics = defaultdict(lambda:defaultdict(str))

ignored_yet = defaultdict(bool)
rubric_yet = defaultdict(bool)

cfg_synonyms = defaultdict(str)

def usage():
    print("So far we only can allow one project at a time defined on the command line.")
    print("If nothing is defined, we look at the current directory, then look in punc.txt for the default project.")
    exit()

def cfg_expand(x):
    if re.search("^[0-9,-]+$", x): return x
    if x in cfg_synonyms: return cfg_synonyms[x]
    if re.search("^[0-9]+,[a-z]$", x): return x
    my_num = "0"
    x0 = x
    if x[0].isdigit():
        x0 = re.sub("^[0-9]+", "", x)
        my_num = re.search("^[0-9]+", x).group()
    if x0 not in cfg_synonyms:
        sys.exit("Unrecognized CFG file shortcut {0} {1}".format(x, x0))
    retval = re.sub("^[0-9]+", my_num, x[0] + cfg_synonyms[x0])
    return retval

def word_to_title(this_word, force=False):
    if this_word in title_words and force == False: return this_word
    if this_word == this_word.lower() and force == False: return this_word.title()
    return this_word[0].upper() + this_word[1:]

def okay_title(w, force_first_letter):
    if "'" in w:
        w = re.sub("'.*", "", w)
    if w == w.upper(): return True
    if w in title_words and not force_first_letter: return True
    return w == w[0].title() + w[1:]

def tack_on_table(x):
    if not x.startswith("table of "):
        return "table of " + x
    return x

def good_rules(my_line, table_rubric, line_count):
    errs = 0
    return_string = my_line
    line_divs = my_line.split("\t")
    orig_string = modified_string = return_string
    for x in table_rubric:
        errs_this_time = 0
        ary = [int(q) for q in x.split(",")]
        col_num = ary[0]
        capitalize_type = ary[1]
        punc_needed = ary[2]
        quotes_needed = ary[3]
        orig_to_check = text_to_check = line_divs[col_num].strip()
        if "[p]" in my_line: continue
        ignore_punc = "[p]" in my_line.lower()
        if not text_to_check.startswith("\""):
            print("Column", col_num, "failed to start with a quote")
            errs += 1
            continue
        num_quotes = text_to_check.count('"')
        if not num_quotes == 2:
            print("Bad # of quotes ({0}) in {1}.", num_quotes, text_to_check)
            errs_this_time += 1
        text_to_check = text_to_check[1:]
        if text_to_check.startswith(" "):
            print("Column", col_num, "had extra starting space")
            errs += 1
        text_to_check = re.sub("\".*", "", text_to_check)
        if quotes_needed == 1:
            if text_to_check.startswith('"') or text_to_check.endswith('"'):
                pass
            else:
                print("Quotes needed but not found in {0}".format(text_to_check))
        elif quotes_needed == -1:
            if text_to_check.startswith('"') or text_to_check.endswith('"'):
                print("Unnecessary quotes found in {0}".format(text_to_check))
        ends_with_punc = re.search("[\?!\.]'?$", text_to_check)
        if not ignore_punc:
            if punc_needed == 1 and not ends_with_punc:
                print("{0} Punctuation needed to end {1}".format(line_count, text_to_check))
                errs += 1
            elif punc_needed == -1 and ends_with_punc:
                print("Extraneous punctuation with {0}".format(text_to_check))
                errs += 1
        text_to_check = re.sub("^(a|the|an) ", "", text_to_check, 0, re.IGNORECASE)
        if capitalize_type == 3:
            if text_to_check.upper() != text_to_check:
                print("Need ALL UPPER for {0}".format(text_to_check))
                errs += 1
                line_divs[col_num] = re.sub("^(\"[^\"]\")", "\1".upper(), line_divs[col_num])
                modified_string = "\t".join(line_divs).strip() + "\n"
        elif capitalize_type == 2:
            word_ary = re.split("[ -]", text_to_check)
            for w in range(0, len(word_ary)):
                first_last = (not w or w == len(word_ary) - 1)
                if not okay_title(word_ary[w], first_last):
                    errs += 1
                    print(line_count, "Need TITLE CASE for {0}->{1} in {2}".format(word_ary[w], word_ary[w].title(), text_to_check))
                    line_divs[col_num] = re.sub("([A-Za-z']+)", lambda x: word_to_title(x.group(), force=first_last), line_divs[col_num].strip())
                    print("New entry:", line_divs[col_num])
                    modified_string = "\t".join(line_divs).strip() + "\n" #?? what about "a possible bug" needs a capitalized
        elif capitalize_type == 1:
            t2 = re.sub("^[a-zA-Z]*", "", text_to_check)
            if t2[0] != t2[0].upper():
                errs += 1
                print("Need STARTING UPPER for {0}".format(text_to_check))
                line_divs[col_num] = re.sub("^\"(a|an|the )?([a-z])+", "\1" + "\2".upper(), line_divs[col_num])
                modified_string = "\t".join(line_divs).strip() + "\n" #?? what about "a possible bug" needs a capitalized
        elif capitalize_type == -1:
            if text_to_check.lower() != text_to_check:
                print("Need ALL LOWER for {0}".format(text_to_check))
                errs += 1
                line_divs[col_num] = re.sub("^(\"[^\"]*\")", lambda x: x.group().lower(), line_divs[col_num])
                modified_string = "\t".join(line_divs).strip() + "\n"
    return (errs, return_string, orig_string != return_string)

def process_file_punc(my_proj, this_file):
    if not os.path.exists(this_file):
        print("Uh oh, {0} does not exist.".format(this_file))
        return
    err_lines = 0
    total_errs = 0
    diffable_lines = 0
    out_file = open(temp_table_file, "w")
    header_next = False
    current_table = ""
    current_rubric = ""
    table_cols = defaultdict(int)
    with open(this_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if header_next:
                out_file.write(line)
                header_next = False
                continue
            if not current_table and line.startswith("table of"):
                current_table = re.sub(" *\[.*", "", line.lower().strip())
                current_table = re.sub(" \(continued\)", "", current_table)
                if current_table in ignores[my_proj]:
                    ignored_yet[current_table] = True
                    #print("IGNORING", current_table, "in", my_proj, "line", line_count)
                    ignore_table = True
                    out_file.write(line)
                    continue
                if current_table not in rubrics[my_proj]:
                    print("WARNING: no rubric for", current_table, "in", my_proj)
                    ignore_table = True
                    out_file.write(line)
                    continue
                rubric_yet[current_table] = True
                current_rubric = rubrics[my_proj][current_table]
                header_next = True
                out_file.write(line)
                continue
            if current_table:
                #if not line.strip() or (line.startswith("[") and line.endswith("]")):
                if not line.strip():
                    current_table = ""
                    ignore_table = False
                    out_file.write(line)
                    continue
                if ignore_table:
                    out_file.write(line)
                    continue
                #print("Rubric for {0}/{1} is {2}".format(my_proj, current_table, current_rubric))
                (this_errs, to_write, sugg_change) = good_rules(line, current_rubric, line_count)
                diffable_lines += sugg_change
                err_lines += (this_errs > 0)
                total_errs += this_errs
                out_file.write(to_write)
                if this_errs: mytools.add_postopen_file_line(this_file, line_count)
                continue
            out_file.write(line)
    out_file.close()
    if diffable_lines:
        print(diffable_lines, "Diffable lines.")
        i7.wm(this_file, temp_table_file)
    elif err_lines:
        print("Errors found, but there are no suggested edits, so not comparing with WinMerge.")
    os.remove(temp_table_file)
    print(err_lines, "line errors", total_errs, "total errors")

def process_project(my_proj):
    if my_proj not in file_list:
        table_file = i7.hdr(my_proj, 'ta')
        print("No FILES= line defined for {0} in {1}. Going with just {2}.".format(my_proj, punc_file, table_file))
        file_list[my_proj] = [ table_file ]
    for x in file_list[my_proj]:
        print("Processing file", x)
        process_file_punc(my_proj, x)
    for x in rubrics[my_proj]:
        if x not in rubric_yet:
            print(x, "had a rubric but wasn't found in the {0} project.".format(my_proj))
    for x in ignores[my_proj]:
        if x not in ignored_yet:
            print(x, "had an ignore flag but wasn't found in the {0} project.".format(my_proj))

def process_punc_cfg(punc_file):
    proj_reading = ""
    global default_proj
    with open(punc_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#") or line.startswith("======"): continue
            if line.startswith(";"): break
            ll = line.lower().strip()
            if line.startswith("VALUE=") or line.startswith("PROJECT="):
                proj_reading = re.sub(".*=", "", ll)
                continue
            if line.startswith("DEFAULT="):
                default_proj = re.sub(".*=", "", ll)
                continue
            if line.startswith("FILES="):
                ltemp = re.sub(".*=", "", ll)
                file_list[proj_reading].append(ltemp)
                continue
            if line.startswith("-"):
                ary = line[1:].strip().split(",")
                for itm in ary:
                    table_name = tack_on_table(itm)
                    ignores[proj_reading].append(table_name)
                #print("Ignoring", ll[1:])
                continue
            if "~" in line:
                lary = ll.split("~")
                cfg_synonyms[lary[0]] = lary[1]
                continue
            if "\t" in line:
                lary = ll.split("\t")
                table_name = tack_on_table(lary[0])
                rubrics[proj_reading][table_name] = [cfg_expand(x) for x in lary[1:]]
                #print("Adding proj {0} rubric {1}".format(proj_reading, lary[0]))
                continue
            if ll: print("CFG file has ignored line", line_count, ll)

punc_file = "c:/writing/dict/punc.txt"

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mytools.nohy(sys.argv[cmd_count])
    if arg in i7.i7x:
        if cur_proj:
            sys.exit("Can't define 2 projects on the command line.")
        cur_proj = i7.i7x[arg]
    else:
        print("Bad command line parameter", arg)
        usage()
    cmd_count += 1

process_punc_cfg(punc_file)

if not cur_proj:
    if not default_proj: sys.exit("You need to specify a default project in the cfg file.")
    print("Setting current project to default project", default_proj)
    cur_proj = default_proj

process_project(cur_proj)

mytools.postopen_files()