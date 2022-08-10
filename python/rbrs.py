#
# rbrs.py: scrambles an RBR file into so many different possibilities
#

import os
import glob
import re
import sys
from itertools import permutations

def proper_constraints(my_permutation, constraints_array):
    for c in constraints_array:
        tries = [int(x) for x in re.split('[<>]', c)]
        first_smaller = my_permutation.index(tries[0]) < my_permutation.index(tries[1])
        if first_smaller != ('<' in c):
            return False
    return True

def controlled_permutations_of(how_many_numbers, max_shuffles):
    overall_count = 0
    initial_array = list(range(0, how_many_numbers))
    constraints_array = my_constraints.split(',')
    for p in permutations(initial_array):
        if proper_constraints(p, constraints_array):
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

def rbr_scramble(my_file, max_shuffles = 120):
    fixed = [ '' ]
    shuffles = [ ]
    overall_index = 0
    in_fixed = True
    bail_before_shuffle = False
    with open(my_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("##RBRSHUFFLESTART="):
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
                continue
            if line.startswith("##RBRSHUFFLEEND="):
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
                continue
            if in_fixed:
                fixed[overall_index] += line
            else:
                shuffles[overall_index] += line
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
    for x in permutation_array:
        x2 = [str(a) for a in x]
        new_file = my_file.replace('reg-', 'reg-scramble{}-'.format(''.join(x2)))
        print(new_file)

def rbr_scramble_all(glob_str):
    my_glob = glob.glob(glob_str)
    for g in my_glob:
        rbr_scramble(os.path.basename(g))

my_constraints = constraints_of("rbr-lljj-thru.txt")

rbr_scramble_all("reg-lljj-thru-*")
sys.exit()