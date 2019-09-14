import sys
import os
import i7
from collections import defaultdict

assigned_project = ""
do_not_commit = defaultdict(int)

def check_commit_includes(f):
    print("=" * 50, "testing", f)
    with open(f) as file:
        for (line_count, line) in enumerate(file, 1):
            if "commit]" in line.lower(): print(line_count, line.rstrip())
            if "[do not commit]" in line.lower() and not line.startswith("["):
                print("Uh oh. You have an uncommented do-not-commit line in story.ni.")
                print("{} {}".format(line_count, line.rstrip()))
                do_not_commit[f] += 1
            if "[must commit]" in line.lower() and line.startswith("["):
                print("Uh oh. You have a commented must-commit line in story.ni.")
                print("{} {}".format(line_count, line.rstrip()))
                do_not_commit[f] += 1
    if f not in do_not_commit:
        print("Do-not-commit tests passed for {}.".format(f))


if not assigned_project:
    if not i7.dir2proj():
        sys.exit("Need to assign a project or be in a valid directory, GitHub or games/inform.")
    my_gh_file = i7.gh_src(i7.dir2proj())
    my_source_file = i7.main_src(i7.dir2proj())

check_commit_includes(my_gh_file)
check_commit_includes(my_source_file)

if len(do_not_commit):
    print("Fix", ', '.join(do_not_commit), "before committing.")
    sys.exit(1)

