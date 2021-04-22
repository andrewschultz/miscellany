#
# punc.py
#
# replaces punc.pl
#
# usage: so far only projects on the command line
# with d/nd debug
# ae/nae for extraneous apostrophe suggestions
# c/nc for copy over or not
#

import i7
import re
import sys
import os
import mytools as mt

from filecmp import cmp
from collections import defaultdict
import mytools as mt
import shutil

import titlecase

debug = False
copy_over = False

mt.title_words.append("y")

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

ALL_CAPS = 4
TITLE_CASE_IGNORE_ARTICLES = 3
TITLE_CASE = 2
SENTENCE_CASE = 1
ALL_LOWER = -1

def usage():
    print("So far we only can allow one project at a time defined on the command line.")
    print("If nothing is defined, we look at the current directory, then look in punc.txt for the default project.")
    print("-nae/-ae disables/enables extraneous apostrophe suggestions")
    print("-d/-nd/-dn toggles debug")
    print("-c/-nc/-cn toggles copy-back-over")
    print("-e = look in config file")
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
        print("Unrecognized CFG file shortcut {0}.".format(x))
        return "!!!"
    retval = re.sub("^[0-9]+", my_num, x[0] + cfg_synonyms[x0])
    return retval

def quoted_to_title(my_string): # this assumes "xxxx" [abc]
    my_ary = my_string.split('"', 2)
    my_ary[1] = titlecase.titlecase(my_ary[1])
    return '"'.join(my_ary)

def okay_title(w, force_first_letter):
    if "'" in w:
        w = re.sub("'.*", "", w)
    if w == w.upper(): return True
    if w in mt.title_words and not force_first_letter: return True
    return w == w[0].title() + w[1:]

def tack_on_table(x):
    if not x.startswith("table of "):
        return "table of " + x
    return x

def apostrophe_imbalance(my_txt):
    if 'aposok' in my_txt:
        return ''
    la = re.findall(r'[^a-zA-Z\.\?!]\'', my_txt)
    left_of_apos = len(la)
    ra = re.findall(r'\'[^a-zA-Z]', my_txt)
    right_of_apos = len(ra)
    lr = left_of_apos - right_of_apos
    if debug and lr:
        print(my_txt, "nontext to left", left_of_apos, "nontext to right", right_of_apos)
    if not lr: return ""
    if lr < 0: return "{0}R".format(-lr)
    return "{0}L".format(lr)

def caps_check(my_string, capitalize_type, line_count):
    if capitalize_type == ALL_CAPS:
        if my_string.upper() != my_string:
            print("Need ALL UPPER for {0}".format(my_string))
            my_string = re.sub("^(\"[^\"]\")", "\1".upper(), my_string)
            return my_string
    elif capitalize_type == TITLE_CASE_IGNORE_ARTICLES:
        temp = quoted_to_title(my_string)
        index = 1
        index += (temp[0] == '"')
        if re.search('^\"?(A |An |The )', temp):
            temp = temp[:index].lower() + temp[index:]
        if temp != my_string:
            print(line_count, "Need TITLE CASE (ignoring leading article) for {0} -> {1}".format(my_string, temp))
        return temp
    elif capitalize_type == TITLE_CASE:
        temp = quoted_to_title(my_string)
        if temp != my_string:
            print(line_count, "Need TITLE CASE for {0}->{1}".format(my_string, temp))
        return temp
    elif capitalize_type == SENTENCE_CASE:
        if my_string[0] != my_string[0].upper():
            print("Need STARTING UPPER for {0}".format(my_string))
        return my_string[0].upper() + my_string[1:]
    elif capitalize_type == ALL_LOWER:
        if my_string.lower() != my_string.lower():
            print("Need ALL LOWER for {0}".format(my_string))
            my_string = my_string.upper()
    return my_string

def apply_table_rules_to_line(my_line, table_rubric, line_count):
    errs = 0
    return_string = my_line
    line_divs = my_line.strip().split("\t")
    orig_string = modified_string = return_string
    for x in table_rubric:
        errs_this_time = 0
        ary = [int(q) for q in x.split(",")]
        col_num = ary[0]
        capitalize_type = ary[1]
        punc_needed = ary[2]
        quotes_needed = ary[3]
        orig_to_check = text_to_check = line_divs[col_num].strip()
        ignore_punc = "[puncok]" in my_line.lower()
        ignore_caps = "[capsok]" in my_line.lower()
        error_printed_this_line_yet = False
        if not text_to_check.startswith("\""):
            print("Column", col_num, "failed to start with a quote")
            errs += 1
            continue
        this_apost = apostrophe_imbalance(text_to_check)
        if this_apost:
            print("Apostrophe imbalance line", line_count, text_to_check, this_apost)
            errs += 1
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
        if not ignore_caps:
            temp = caps_check(line_divs[col_num], capitalize_type, line_count)
            if temp != line_divs[col_num]:
                line_divs[col_num] = temp
                modified_string = "\t".join(line_divs).strip() + "\n"
                errs += 1
        if this_apost and modified_string == orig_string and suggest_apostrophes:
            modified_string = this_apost + modified_string
    return (errs, modified_string, orig_string != modified_string)

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
                if current_rubric:
                    (this_errs, to_write, sugg_change) = apply_table_rules_to_line(line, current_rubric, line_count)
                    diffable_lines += sugg_change
                    err_lines += (this_errs > 0)
                    total_errs += this_errs
                    out_file.write(to_write)
                    if this_errs: mt.add_postopen_file_line(this_file, line_count)
                continue
            out_file.write(line)
    out_file.close()
    if diffable_lines:
        print(diffable_lines, "Diffable lines.")
        mt.wm(this_file, temp_table_file)
    elif err_lines:
        print("Errors found, but there are no suggested edits, so not comparing with WinMerge.")
    if copy_over:
        shutil.move(temp_table_file, this_file)
    else:
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
                    table_name = tack_on_table(itm).strip()
                    ignores[proj_reading].append(table_name)
                #print("Ignoring", ll[1:])
                continue
            if "~" in line:
                lary = ll.split("~")
                left_ary = lary[0].split(",")
                for l in left_ary:
                    if l in cfg_synonyms:
                        print("Redefining CFG synonym <{0}> at line {1} in {2}.".format(l.upper(), line_count, punc_file))
                        mt.npo(punc_file, line_count)
                    cfg_synonyms[l] = lary[1]
                continue
            if "\t" in line:
                lary = ll.split("\t")
                table_name = tack_on_table(lary[0])
                rubrics[proj_reading][table_name] = [cfg_expand(x) for x in lary[1:]]
                if "!!!" in rubrics[proj_reading][table_name]:
                    print("Uh oh, bad CFG values at {0} line {1}.".format(punc_file, line_count))
                    mt.npo(punc_file, line_count)
                #print("Adding proj {0} rubric {1}".format(proj_reading, lary[0]))
                continue
            if ll: print("CFG file has ignored line", line_count, ll)

punc_file = "c:/writing/dict/punc.txt"

suggest_apostrophes = True

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in i7.i7x:
        if cur_proj:
            sys.exit("Can't define 2 projects on the command line.")
        else:
            print("Cmd line parameter {} leads to project {}.".format(arg, cur_proj))
        cur_proj = i7.i7x[arg]
    elif arg == 'ae': suggest_apostrophes = True
    elif arg == 'nae': suggest_apostrophes = False
    elif arg == 'nd' or arg == 'dn': debug = False
    elif arg == 'd': debug = True
    elif arg == 'c': copy_over = True
    elif arg == 'e': mt.npo(punc_file)
    elif arg == 'nc' or arg == 'cn': copy_over = False
    else:
        print("Bad command line parameter", arg)
        usage()
    cmd_count += 1

process_punc_cfg(punc_file)

dir_default = i7.dir2proj()

if not cur_proj:
    if not default_proj and not dir_default: sys.exit("You need to specify a default project in the cfg file.")
    if dir_default:
        print("Setting current project to project defined by path", dir_default)
    elif default_proj:
        print("Setting current project to default project", default_proj)
    else:
        print("This should never happen, but I couldn't guess what project you wanted to run. Bailing.")
        sys.exit()
    cur_proj = default_proj

process_project(cur_proj)

mt.postopen_files()