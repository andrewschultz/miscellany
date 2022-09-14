#
# rpl.py: extension file replacement
#
# C:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz
# linked to GitHub
#

import os
import sys
import glob
import i7
import mytools as mt
import colorama

file_list = []

print_command = True
run_command = False

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'p':
        print_command = True
    elif arg == 'r':
        run_command = True
    elif arg in ( 'rn', 'nr' ):
        run_command = False
    elif arg in ( 'pn', 'np' ):
        print_command = False
    elif arg in ( 'ro', 'or' ):
        run_command = True
        print_command = False
    elif arg in ( 'po', 'op' ):
        run_command = False
        print_command = True
    elif i7.proj2dir(arg):
        print(colorama.Fore.CYAN + "Changing directory to {}.".format(arg) + colorama.Style.RESET_ALL)
        os.chdir(i7.proj2dir(arg, to_github = True))
    else:
        file_list.append(arg)
    cmd_count += 1

if not len(file_list):
    file_list = glob.glob(os.getcwd() + "\\*.i7x")

if print_command and not run_command:
    print(colorama.Fore.MAGENTA + "REMEMBER TO TYPE -R TO RUN THINGS" + colorama.Style.RESET_ALL)

for x in file_list:
    basename = os.path.basename(x)
    normname = os.path.normpath(x)
    fromname = os.path.join(i7.ext_dir, basename)
    if os.path.exists(fromname):
        print(colorama.Fore.RED + "UH OH", fromname, "exists so not mapping to", normname + mt.WTXT)
        continue
    if not os.path.exists(normname):
        print(colorama.Fore.RED + "UH OH", normname, "does not exist as target", normname + mt.WTXT)
        continue
    my_command = 'mklink "{}" "{}"'.format(fromname, normname)
    if print_command:
        print((colorama.Fore.GREEN if run_command else colorama.Fore.YELLOW) + my_command + mt.WTXT)
    if run_command:
        os.system(my_command)
