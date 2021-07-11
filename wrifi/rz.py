# rz.py: grabs text from rhymezone

import glob
import os
import re
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
import mytools as mt

rz_out = "c:/writing/temp/rz-out.txt"
rz_backup = "c:/writing/temp/rz-back.txt"
rz_cache = "c:/writing/temp/rz-cache.txt"
rz_cfg = "c:/writing/scripts/rz-cfg.txt"
words_to_rhyme = []

my_word = ''

use_cache = False
to_web = False
append_text = False
backup_prev = True

from_local = to_local = False

cmd_count = 1

def usage():
    print("a appends to the output file. Otherwise, we overwrite it.")
    print("b backs up, nb/bn disables backup. Default is backup.")
    print("c uses cache file already present, shortcircuiting other options.")
    print("o/ol/lo opens last output, oc/co opens cache, ob/bo opens backup. Combine to open multiple files.")
    print("w opens the URL on the web for rhymes/almost-rhymes.")
    print("l tries to do things locally. lf/fl reads from local files, and lt/tl writes to them. L combines them.")
    print()
    print("You can type in as many potential-rhyme words as you want.")
    sys.exit()

def read_cfg_defaults():
    global backup_prev
    global use_cache
    global from_local
    global to_local
    global to_web
    with open(rz_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            (prefix, data) = mt.cfg_to_data(line)
            if prefix == 'backup':
                backup_prev = mt.truth_state_of(data)
            elif prefix == 'cache':
                use_cache = mt.truth_state_of(data)
            elif prefix == 'from_local':
                from_local = mt.truth_state_of(data)
            elif prefix == 'to_local':
                to_local = mt.truth_state_of(data)
            elif prefix in ( 'web', 'to_web' ):
                to_web = mt.truth_state_of(data)
            else:
                print("CFG bad data line {}: {}".format(line_count, line.strip()))

def see_about_local(word_array, file_name):
    return_list = []
    word_from_file = re.sub(".*-", "", file_name)
    word_from_file = re.sub("\..*", "", word_from_file)
    if word_from_file in word_array:
        return_list.append(word_from_file)
    with open(file_name) as file:
        for (line_count, line) in enumerate (file, 1):
            if 'syllable' not in line:
                continue
            l0 = re.sub(".*syllable(s):", "", line.strip().lower())
            ary = re.split(", +", l0)
            return_list.extend(list(set(word_array) & set(ary)))
    if len(return_list) > 0:
        print(', '.join(return_list), "in", file_name)
        mt.npo(file_name, bail = False)
    return return_list

def url_of(this_word, batch_convert = False):
    my_url = "https://rhymezone.com/r/rhyme.cgi?Word={}&typeofrhyme=perfect&org1=syl&org2=l&org3=y".format(this_word)
    if batch_convert:
        my_url = my_url.replace("&", "^&")
    return my_url

def org_raw_rhyme_text(my_text, my_word):
    my_lines = my_text.splitlines()

    read_syllables = False
    any_syllables = False
    out_string = ''

    for x in my_lines:
        if re.search("^[0-9] syllable", x):
            read_syllables = True
            any_syllables = True
        x = x.strip()
        if 'almost rhyme' in x.lower() or 'more ideas' in x.lower():
            read_syllables = False
        if 'words and phrases that' in x.lower():
            out_string += "\n" + x
        if read_syllables:
            if 'syllable' in x:
                out_string += "\n" + x + " "
            else:
                out_string += x.replace(',', ', ')

    out_string = '=========================Rhymes for {}=========================\n'.format(my_word) + out_string.lstrip()

    return out_string

def send_to_cache(w, out_file = rz_cache, straighten_before_caching = True):
    url = url_of(w)

    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text().encode('ascii', 'ignore').decode('ascii')
    if straighten_before_caching:
        text = org_raw_rhyme_text(text, w)
    f = open(out_file, "w")
    f.write(text)
    f.close()

def process_cache(my_word, reset = False):
    outputting = "w" if reset else "a"
    f = open(rz_cache, "r")
    text = org_raw_rhyme_text(f.read(), my_word)

    if not text:
        sys.exit("Failed to read anything.")

    f = open(rz_out, outputting)
    f.write(text.strip() + "\n")
    f.close()

read_cfg_defaults()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'w':
        to_web = True
    elif arg == 'c':
        use_cache = True
    elif arg == 'a':
        append_text = True
    elif arg == 'b':
        backup_prev = True
    elif arg == 'l':
        to_local = True
        from_local = True
    elif arg in ( 'lf', 'fl' ):
        from_local = True
        to_local = False
    elif arg in ( 'lt', 'tl' ):
        to_local = True
        from_local = False
    elif arg in ( 'ln', 'nl' ):
        to_local = False
        from_local = False
    elif arg in ( 'nb', 'bn' ):
        backup_prev = False
    elif arg in ( 'o', 'ol', 'lo' ):
        mt.npo(rz_out)
    elif arg in ( 'ob', 'bo' ):
        mt.npo(rz_backup)
    elif arg in ( 'co', 'oc' ):
        mt.npo(rz_cache)
    elif re.search('^[obcl]{2,}$', arg):
        if 'b' in arg:
            mt.npo(rz_backup, bail=False)
        if 'c' in arg:
            mt.npo(rz_cache, bail=False)
        if 'l' in arg:
            mt.npo(rz_out, bail=False)
        sys.exit()
    elif arg == '?':
        usage()
    elif len(arg) == 1:
        usage("Bad argument {}".format(arg))
    else:
        words_to_rhyme.append(arg)
    cmd_count += 1

if to_web:
    for w in words_to_rhyme:
        url = url_of(w, batch_convert = True)
        print("Hunting for rhymes of", w)
        os.system("start {}".format(url))
    sys.exit()

if from_local:
    x = glob.glob("c:/writing/temp/rz-locals-*")
    for file in x:
        temp = see_about_local(words_to_rhyme, file)
        if temp:
            for t in temp:
                words_to_rhyme.remove(t)
    if len(words_to_rhyme) == 0:
        sys.exit("All rhymes were found locally.")

if use_cache:
    f = open(rz_cache, "r")
    text = f.read()
    f.close()
    for x in text.split("\n"):
        if x.startswith("RhymeZone: "):
            my_word = ' '.join(x.split(' ')[1:-1])
            print("Found rhymable word {} in cache.".format(my_word))
            break
    if not my_word:
        print("WARNING: could not find rhymable word in cache. Going with UNDEFINED.")
        my_word = "UNDEFINED"
    process_cache(my_word, reset = not append_text)
    sys.exit()

if len(words_to_rhyme) == 0:
    sys.exit("No rhymes given.")

if backup_prev:
    f = open(rz_out, "r")
    my_text = f.read()
    f.close()
    f = open(rz_backup, "w")
    f.write(my_text)
    f.close()

for w in words_to_rhyme:
    if to_local:
        my_file = "c:/writing/temp/rz-locals-{}.txt".format(w)
        if os.path.exists(my_file):
            print(my_file, "exists.")
            words_to_rhyme.remove(t)
            temp = see_about_local(words_to_rhyme, my_file)
            if temp:
                for t in temp:
                    words_to_rhyme.remove(t)
                continue
            continue
        for q in glob.glob("c:/writing/temp/rz-locals-*.txt"):
            temp = see_about_local(words_to_rhyme, my_file)
            if temp:
                for t in temp:
                    words_to_rhyme.remove(t)
                continue
        send_to_cache(w, my_file, straighten_before_caching = True)
    else:
        if not append_text:
            f = open(rz_out, "w")
            f.close()
            append_text = True
        send_to_cache(w)
        process_cache(w, reset = False)

mt.npo(rz_out)