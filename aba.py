# aba.py
# andrew-basic stuff (reused comparing other files)

def aba_usage():
    print("File_to_alf, file_alf_compare, file_char_size, file_line_len are functions")
    sys.exit()

def file_to_alf(fname, out_name, ignore_blanks = True):
    fo = open(fname, "rU")
    fl = sorted(fo.readlines())
    if ignore_blanks: fl = list(filter(None, [x.strip() for x in fl]))
    f2 = open(out_name, "w")
    f2.write("\n".join(fl) + "\n")

def file_alf_compare(f1, f2, show_win_merge = False):
    a1 = "c:/writing/temp/alf-1.txt"
    a2 = "c:/writing/temp/alf-2.txt"
    file_to_alf(f1, a1)
    file_to_alf(f2, a2)
    if show_win_merge:
        print(f1, "vs.", f2, "alphabetical comparison")
        os.system("wm \"{:s}\" \"{:s}\"".format(a1, a2))
    return cmp(a1, a2)

def file_char_size(fname):
    len = 0
    with open(fname) as file:
        for line in file:
            len += len(line)
    return len

def file_line_len(fname, count_blanks = False):
    blanks = 0
    with open(fname) as f:
        for i, l in enumerate(f, 1):
            if not count_blanks and not l.strip(): blanks += 1
            pass
    return i + blanks

if "aba.py" in main.__file__:
    if len(sys.argv) > 1:
        if sys.argv[1] == '?': aba_usage()
    print("Not a valid argument for running the aba module directly. ? is the only one.")
    sys.exit()
