import re
import sys

from collections import defaultdict

# ary = ['roiling', 'shuffling']
ary = ['shuffling']

files = { 'shuffling': [ 'reg-sa-thru.txt' ] }

write_file = False

if len(sys.argv) > 1:
    if sys.argv[1] == 'w':
        write_file = True

def mister(a):
    need_test = defaultdict(int)
    found = defaultdict(bool)
    source_dir = "c:/games/inform/%s.inform/Source/" % a
    in_file = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/%s mistakes.i7x" % a
    count = 0
    with open(in_file) as file:
        for line in file:
            count = count + 1
            l = line.lower().strip()
            if re.search("understand.*as a mistake", l):
                l = re.sub("understand +\"", "", l)
                l = re.sub("\" as a mistake.*", "", l)
                l = re.sub("\"", "", l)
                l = re.sub(" and ", "/", l)
                need_test[l] = count
                found[l] = False
    for p in sorted(need_test.keys(), key=need_test.get):
        print(p, need_test[p])
    x = files[a]
    extra_text = defaultdict(str)
    for fi in x:
        with open(source_dir + fi) as file:
            count = 0
            err_count = 0
            for line in file:
                count = count + 1
                if line.startswith("#"):
                    test_note = re.sub("^#mistake (re)?test for ", "", line.strip().lower())
                elif line.startswith('>'):
                    ll = re.sub("^>", "", line.strip().lower())
                    if ll != test_note:
                        if ll in need_test.keys():
                            err_count = err_count + 1
                            print("({:4d}) {:14s} Line {:4d} #mistake test for {:s}".format(err_count, fi, count, ll))
                            extra_text[count] = ll
                            found[l] = True
                    ll = ""
                else:
                    ll = ""
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

for e in ary:
    mister(e)
