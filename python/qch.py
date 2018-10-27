import os
from collections import defaultdict

need_readme = 0
files_need_label = 0
total_labels = 0

def readme_process(readme, files_to_see):
    global files_need_label
    global total_labels
    f2c = defaultdict(bool)
    for q in files_to_see:
        f2c[q] = True
    with open(readme) as file:
        for line in file:
            for q in list(f2c):
                if q in line: f2c.pop(q, None)
    if len(f2c):
        files_need_label += 1
        total_labels += len(f2c.keys())
        print(readme, "NEEDS TO LABEL", len(f2c.keys()), '\n        ', ' / '.join(f2c.keys()))
    else:
        print(readme, "up to date.")

def list_dirs(a):
    global need_readme
    any_pl_py = []
    got_readme = False
    perl_count = 0
    python_count = 0
    for x in os.listdir(a):
        if x == '.' or x == '..' or x == '.git' or x == 'habitica' or x == 'lawless-legends' or x == 'perlmaven' or x.startswith('trizbort'): continue
        x2 = os.path.join(a, x)
        if os.path.isdir(x2):
            #print("Recursing to", x2)
            list_dirs(x2)
        if x.endswith("pl") or x.endswith("py"):
            if x.endswith("pl"): perl_count += 1
            else: python_count += 1
            any_pl_py.append(x)
        if x.lower() == 'readme.md': got_readme = True
    if len(any_pl_py):
        if got_readme == False:
            print(a, "may need readme for", ' / '.join(any_pl_py), 'as it has', perl_count, 'perl and', python_count, 'python file(s)')
            need_readme += 1
        else:
            readme_process(os.path.join(a, "readme.MD"), any_pl_py)

list_dirs(".")
print("Need readme", need_readme)
print("Need labels", files_need_label, "total labels", total_labels)
