import re
import sys
import glob

from collections import defaultdict

# ary = ['roiling', 'shuffling']
# ary = ['shuffling']
ary = ['roiling']

short = { 'shuffling':'sa', 'roiling':'roi' }
files = { 'shuffling': ['c:/games/inform/shuffling.inform/source/reg-sa-thru.txt'],
  'roiling': ['c:/games/inform/roiling.inform/source/reg-roi-thru.txt', 'c:/games/inform/roiling.inform/source/reg-roi-demo-dome-nudges.txt'] }

write_file = False
verbose = False

if len(sys.argv) > 1:
    if sys.argv[1] == 'w':
        write_file = True

def mister(a):
    need_test = defaultdict(int)
    mistake_text = defaultdict(str)
    cmd_text = defaultdict(str)
    found = defaultdict(bool)
    comment_found = defaultdict(bool)
    source_dir = "c:/games/inform/%s.inform/Source/" % a
    in_file = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/%s mistakes.i7x" % a
    count = 0
    special_def = ''
    with open(in_file) as file:
        for line in file:
            count = count + 1
            l = line.strip()
            if l.startswith("[def="):
                special_def = re.sub("^\[def=", "", l)
                special_def = re.sub("\].*", "", special_def)
                continue
            if re.search("understand.*as a mistake", l, re.IGNORECASE):
                cmd = re.sub("understand +\"", "", l)
                cmd = re.sub("\" as a mistake.*", "", cmd)
                cmd = re.sub("\"", "", cmd)
                cmd = re.sub(" and ", "/", cmd)
                if special_def != '':
                    x = special_def
                else:
                    x = cmd
                # print("OK,", x)
                cmd_text[x] = cmd
                mistake_text[x] = re.sub(".*\(\"", "", l)
                mistake_text[x] = re.sub("\"\).*", "", mistake_text[x])
                if x in need_test.keys():
                    print('Uh oh,', x, 'duplicates line', need_test[x], 'at line', count)
                need_test[x] = count
                found[x] = False
                comment_found[x] = False
            special_def = ''
    # for p in sorted(need_test.keys(), key=need_test.get):
        # print(p, need_test[p])
    # files = glob.glob(source_dir + "reg-" + short[a] + "-thru*.txt")
    files = [ '{:s}reg-{:s}-thru.txt'.format(source_dir, short[a]) ]
    extra_text = defaultdict(str)
    for fi in files:
        short_fi = re.sub(".*[\\\/]", "", fi)
        retest = False
        with open(fi) as file:
            count = 0
            err_count = 0
            test_note = ""
            for line in file:
                count = count + 1
                if retest == True:
                    retest = False
                    # print("Skipping", line.strip())
                    continue
                if line.startswith("#mistake retest"):
                    retest = True
                    continue
                if line.startswith("#mistake text") or line.startswith("#mistake retext"):
                    print('Line', count, 'says text not test.')
                    continue
                if line.startswith("##mistake"):
                    print('Line', count, 'says text not test.')
                    continue
                retest = False
                if line.startswith("#mistake "):
                    test_note = re.sub("^#mistake test for ", "", line.strip().lower())
                    if comment_found[test_note]:
                        print('Duplicate mistake test for', test_note, 'at line', count, '(reroute to mistake retest?)')
                        err_count = err_count + 1
                    # print("Got", test_note)
                    comment_found[test_note] = True
                elif line.startswith('>'):
                    ll = re.sub("^>", "", line.strip().lower())
                    if ll != test_note:
                        if ll in need_test.keys():
                            if found[ll] is False:
                                err_count = err_count + 1
                                print("({:4d}) {:14s} Line {:4d} #mistake test for {:s}".format(err_count, fi, count, ll))
                            extra_text[count] = ll
                            found[ll] = True
                    if test_note in found.keys():
                        found[test_note] = True
                    ll = ""
                    test_note = ""
                else:
                    ll = ""
                    test_note = ""
        if write_file:
            out_file = source_dir + "pro" + fi
            fout = open(out_file, "w")
            print("Writing", out_file)
            with open(source_dir + fi) as file:
                count = 0
                for line in file:
                    count = count + 1
                    if count in extra_text.keys():
                        fout.write("##mistake test for" + extra_text[count] + "\n")
                    fout.write(line)
            fout.close()
    find_count = 0
    for f in sorted(found.keys(), key=need_test.get):
        if found[f] == False:
            find_count = find_count + 1
            if verbose:
                print('#mistake test for {:80s}{:4d} to find({:d})'.format(f, find_count, need_test[f]))
            else:
                print('#{:4d} to find({:d})'.format(find_count, need_test[f]))
                print('#mistake test for', f)
            for ct in cmd_text[f].split('/'):
                print('>' + re.sub("\[text\]", "zozimus", ct))
                print(mistake_text[f])
            print()

for e in ary:
    mister(e)
