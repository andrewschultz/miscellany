#
# rbrs.py: scrambles an RBR file into so many different possibilities
#

import os
import glob
import re
import sys
from itertools import permutations

import mytools as mt

only_one_file = True
add_creation_mark = True

def usage(my_arg = '')
    print("Bad argument", my_arg)
    print('=' * 50)
    print()
    print("Possible arguments:")
    print("a = all files, o = only one")
    sys.exit()

def controlled_permutations_of(how_many_numbers, max_shuffles):
    overall_count = 0
    initial_array = list(range(0, how_many_numbers))
    constraints_array = my_constraints.split(',')
    for p in permutations(initial_array):
        if mt.proper_constraints(p, constraints_array):
            l = list(p)
            if l == initial_array:
                continue
            yield l
            overall_count += 1
            if overall_count == max_shuffles:
                print("Max shuffles reached, returning.")
                return
    return

def constraints_of(my_file):
    rbr_constraints_string = ''
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("##RBRCONSTRAINTS="):
                if rbr_constraints_string:
                    print("WARNING line", line_count, "has duplicate RBRSCRAMBLE. There should only be one. Bailing.")
                    bail_before_shuffle = True
                else:
                    rbr_constraints_string = re.sub(".*=", "", line.strip())
                continue
    if not rbr_constraints_string:
        print("WARNING there is no constraints string in", my_file)
    return rbr_constraints_string

def should_print(my_ary, my_permutation):
    for a in my_ary:
        if '>' in a:
            a2 = a.split(">")
            if my_permutation.index(int(a2[0])) < my_permutation.index(int(a2[1])):
                return False
        elif '<' in a:
            a2 = a.split("<")
            if my_permutation.index(int(a2[0])) > my_permutation.index(int(a2[1])):
                return False
    return True

def modified_output(my_raw_text, my_permutation):
    return_string = ''
    text_array = my_raw_text.split("\n")
    this_line_out = True
    for t in text_array:
        if t.startswith("##RBRS-SHUFFLECONDITION="):
            t_data = re.sub("^.*?=", "", t)
            if t_data == '!':
                this_line_out = not this_line_out
            else:
                ary = t_data.split(",")
                this_line_out = should_print(ary, my_permutation)
            continue
        if this_line_out:
            return_string += t + "\n"
    return return_string

def rbr_scramble(my_file, max_shuffles = 120):
    fixed = [ '' ]
    shuffles = [ ]
    overall_index = 0
    in_fixed = True
    bail_before_shuffle = False
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.startswith("##RBRS-"):
                if in_fixed:
                    fixed[overall_index] += line
                else:
                    shuffles[overall_index] += line
                continue
            (prefix, data) = mt.cfg_data_split(line.strip(), lowercase_prefix = False)
            if prefix == '##RBRS-SHUFFLESTART':
                if not in_fixed:
                    print("WARNING line", line_count, "tries to SHUFFLESTART in a shuffle. Bailing.")
                    bail_before_shuffle = True
                try:
                    my_number = int(re.sub(".*=", "", line.strip()))
                except:
                    print("WARNING line", line_count, "needs a number after SHUFFLESTART=")
                    bail_before_shuffle = True
                if my_number != overall_index:
                    print("WARNING line", line_count, "needs", overall_index, "after SHUFFLESTART=")
                    bail_before_shuffle = True
                in_fixed = False
                shuffles.append('')
            elif prefix == '##RBRS-SHUFFLEEND':
                if in_fixed:
                    print("WARNING line", line_count, "tries to SHUFFLEEND outside a shuffle. Bailing.")
                    bail_before_shuffle = True
                try:
                    my_number = int(re.sub(".*=", "", line.strip()))
                except:
                    print("WARNING line", line_count, "needs a number after SHUFFLEEND=")
                    bail_before_shuffle = True
                if my_number != overall_index:
                    print("WARNING line", line_count, "needs", overall_index, "after SHUFFLEEND=")
                    bail_before_shuffle = True
                fixed.append('')
                overall_index += 1
                in_fixed = True
            elif prefix == '##RBRS-SHUFFLECONDITION':
                if in_fixed:
                    print("WARNING line", line_count, "tries to SHUFFLECONDITION outside a shuffle. Bailing.")
                    bail_before_shuffle = True
                else:
                    shuffles[overall_index] += line
            else:
                print("WARNING unrecognized rbrs- prefix line {} = {}".format(line_count, prefix))
    if overall_index < 2:
        print("WARNING overall index was 0, so we cannot test permutations.")
        bail_before_shuffle = True
    if not in_fixed:
        print("We ended in a shuffle area. Please close it off with ####RBRSHUFFLEEND=.")
        bail_before_shuffle = True
    if bail_before_shuffle:
        print("Fix errors before shuffling. We want to make sure what's meant to be shuffled, is.")
        return
    permutation_array = list(controlled_permutations_of(overall_index, max_shuffles))
    for this_perm in permutation_array:
        x2 = [str(a) for a in this_perm]
        file_array = my_file.split('-')
        file_array.insert(2, 'scramble')
        file_array.insert(3, ''.join(x2))
        new_file = '-'.join(file_array)
        print("Writing", new_file)
        file_string = ''
        f = open(new_file, "w")
        if add_creation_mark:
            shuffle_ary = shuffles.split("\n")
            shuffle_ary.insert(1, "# created with rbrs.py")
            shuffles = '\n'.join(shuffle_ary)
        for x in range(0, len(shuffles)):
            f.write(fixed[x])
            f.write(modified_output(shuffles[this_perm[x]], this_perm))
        f.write(fixed[-1])
        f.close()
    if only_one_file:
        sys.exit()

def rbr_scramble_all(glob_str):
    my_glob = glob.glob(glob_str)
    for g in my_glob:
        rbr_scramble(os.path.basename(g))

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'a':
        only_one_file = False
    elif arg == 'o':
        only_one_file = True
    elif mt.alfmatch(arg, 'cmn'):
        add_creation_mark = False
    elif arg in ( 'cm', 'mc' ):
        add_creation_mark = True
    else:
        usage(arg)
    cmd_count += 1

my_constraints = constraints_of("rbr-lljj-thru.txt")

rbr_scramble_all("reg-lljj-thru-*")
sys.exit()