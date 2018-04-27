import re
import sys
import glob

from collections import defaultdict

# ary = ['roiling', 'shuffling']
# ary = ['shuffling']
ary = ['ailihphilia']

srev = defaultdict(str)
condition = defaultdict(str)

short = { 'shuffling':'sa', 'roiling':'roi', 'ailihphilia':'ail' }

def usage():
    print("-w/-nw = write or don't")
    print("-c/-nc = write conditions or don't")
    print("-p/-np = print or don't")
    print("-po/-wo = print or write only")
    print("Other arguments are the project name, short or long")
    exit()

for x in short:
    srev[short[x]] = x

def to_full(a):
    if a in srev.keys(): return srev[a]
    if a in short.keys(): return a
    print(a, "not a project with a recognized mistake file.")
    exit()

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
                                if print_output: print("({:4d}) {:14s} Line {:4d} #mistake test for {:s}".format(err_count, fi, count, ll))
                            extra_text[count] = ll
                            ll2 = re.sub(".*when", "", line.strip().lower())
                            condition[count] = ll2
                            found[ll] = True
                    if test_note in found.keys():
                        found[test_note] = True
                    ll = ""
                    test_note = ""
                else:
                    ll = ""
                    test_note = ""
        if write_file:
            out_file = source_dir + "pro-" + short_fi
            fout = open(out_file, "w")
            print("Writing", out_file)
            mistakes_added = 0
            with open(fi) as file:
                count = 0
                for line in file:
                    count = count + 1
                    if count in extra_text.keys():
                        fout.write("##mistake test for " + extra_text[count] + "\n")
                        if print_condition:
                            fout.write("##conditions " + condition[count])
                        mistakes_added = mistakes_added + 1
                    fout.write(line)
            fout.close()
            print(mistakes_added, "total mistakes added.")
    find_count = 0
    for f in sorted(found.keys(), key=need_test.get):
        if found[f] == False:
            find_count = find_count + 1
            if print_output:
                if verbose:
                    print('#mistake test for {:80s}{:4d} to find({:d})'.format(f, find_count, need_test[f]))
                else:
                    print('#{:4d} to find({:d})'.format(find_count, need_test[f]))
                    print('#mistake test for', f)
                if print_condition:
                    print("##conditions", condition[f])
                for ct in cmd_text[f].split('/'):
                    print('>' + re.sub("\[text\]", "zozimus", ct))
                    print(mistake_text[f])
                print()

files = { 'shuffling': ['c:/games/inform/shuffling.inform/source/reg-sa-thru.txt'],
  'roiling': ['c:/games/inform/roiling.inform/source/reg-roi-thru.txt', 'c:/games/inform/roiling.inform/source/reg-roi-demo-dome-nudges.txt'],
  'ailihphilia': ['c:/games/inform/roiling.inform/source/reg-ail-thru.txt' ]
}

write_file = False
print_output = True
verbose = False
print_condition = True

if len(sys.argv) > 1:
    count = 1
    while count < len(sys.argv):
        arg = sys.argv[count]
        if arg[0] == '-': arg = arg[1:]
        if arg == 'w':
            write_file = True
        elif arg == 'nw':
            write_file = False
        elif arg == 'c':
            print_condition = True
        elif arg == 'nc':
            print_condition = False
        elif arg == 'wo':
            write_file = True
            print_output = False
        elif arg == 'np':
            print_output = False
        elif arg == 'p':
            print_output = True
        elif arg == 'po':
            print_output = True
            write_file = False
        else:
            print(count, arg)
            atemp = arg.split(',')
            ary = [to_full(x) for x in atemp]
        count = count + 1

if not write_file and not print_output:
    print("You need to write a file or print output.")
    exit()

for e in ary:
    mister(e)
