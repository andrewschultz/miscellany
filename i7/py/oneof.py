#
# oneof.py
# python script to emulate Inform's "one of" behavior
#
# started 2021-12-17
#

from collections import defaultdict
from random import random, shuffle
import re

sample_data_file = "c:/writing/scripts/oneof.txt"

oneof_keywords = [ 'cycling', 'stopping', 'in random order', 'then at random', 'purely at random', 'then purely at random', 'sticky random', 'decreasingly likely', 'increasingly likely' ]

ONEOF_CYCLING = 0 # 0 1 2 3 0 1 2 3
ONEOF_STOPPING = 1 # 0 1 2 3 3 3 3
ONEOF_RANDOM_ORDER = 2 # random, but no repetitions
ONEOF_THEN_AT_RANDOM = 3 # in sequence, then random, but no repetitions
ONEOF_PURELY_AT_RANDOM = 4 # random, potential repetitions
ONEOF_THEN_PURELY_AT_RANDOM = 5 # in sequence, then random
ONEOF_STICKY_RANDOM = 6 # 7, 7, 7, 7 or 8, 8, 8, 8
ONEOF_DECREASINGLY_LIKELY = 7
ONEOF_INCREASINGLY_LIKELY = 8

class one_of:
    string_array = []
    string_index = 0
    one_of_type = ONEOF_CYCLING
    need_first_time_through = False
    got_first_time_through = False
    first_chosen_yet = False

    def __init__(self, my_array, my_type):
        self.string_array = my_array
        self.one_of_type = my_type
        if my_type == ONEOF_STICKY_RANDOM or my_type == ONEOF_RANDOM_ORDER:
            shuffle(self.string_array)
        if my_type == ONEOF_THEN_AT_RANDOM or my_type == ONEOF_THEN_PURELY_AT_RANDOM:
            need_first_time_through = True
        return

my_oneofs = defaultdict(one_of)

def weighted_choice(my_array_l, ascending = True):
    totals = (my_array_l * (my_array_l + 1)) // 2
    x = int(random() * totals)
    current_compare_val = 1
    increment_val = 1
    my_index = 0
    while 1:
        if x < current_compare_val:
            break
        my_index += 1
        increment_val += 1
        current_compare_val += increment_val
    if ascending:
        return my_index
    else:
        return my_array_l - 1 - my_index

def print_one_of(x):
    this_one_of = my_oneofs[x]
    if this_one_of.one_of_type == ONEOF_STOPPING and this_one_of.string_index == len(this_one_of.string_array) - 1:
        retval = this_one_of.string_array[this_one_of.string_index]
    elif not this_one_of.got_first_time_through and (this_one_of.one_of_type == ONEOF_THEN_AT_RANDOM or this_one_of.one_of_type == ONEOF_THEN_PURELY_AT_RANDOM):
        retval = this_one_of.string_array[this_one_of.string_index]
        this_one_of.string_index += 1
        if this_one_of.string_index == len(this_one_of.string_array):
            shuffle(this_one_of.string_array)
            this_one_of.got_first_time_through = True
            this_one_of.string_index = 0
    elif this_one_of.one_of_type == ONEOF_STICKY_RANDOM:
        if not this_one_of.first_chosen_yet:
            this_one_of.first_chosen_yet = True
            this_one_of.string_index = int(random() * len(this_one_of.string_array))
        retval = this_one_of.string_array[this_one_of.string_index]
    elif this_one_of.one_of_type == ONEOF_DECREASINGLY_LIKELY or this_one_of.one_of_type == ONEOF_INCREASINGLY_LIKELY:
        this_one_of.string_index = weighted_choice(len(this_one_of.string_array), ascending = this_one_of.one_of_type == ONEOF_INCREASINGLY_LIKELY)
        retval = this_one_of.string_array[this_one_of.string_index]
    elif this_one_of.one_of_type == ONEOF_PURELY_AT_RANDOM or this_one_of.one_of_type == ONEOF_THEN_PURELY_AT_RANDOM:
        if this_one_of.first_chosen_yet:
            this_one_of.string_index += 1 + int(random() * (len(this_one_of.string_array) - 1))
            this_one_of.string_index %= len(this_one_of.string_array)
        else:
            this_one_of.first_chosen_yet = True
            this_one_of.string_index = int(random() * len(this_one_of.string_array))
        retval = this_one_of.string_array[this_one_of.string_index]
    else: # everything else should be, or degenerate to, CYCLING
        retval = this_one_of.string_array[this_one_of.string_index]
        this_one_of.string_index += 1
        if this_one_of.string_index == len(this_one_of.string_array):
            this_one_of.string_index = 0
    return retval

with open(sample_data_file) as file:
    for (line_count, line) in enumerate (file, 1):
        if line.startswith(";"):
            break
        if line.startswith("#"):
            continue
        line = line.rstrip()
        if line.startswith("$"):
            if not '=' in line:
                print("Line {} needs = since it starts with $.".format(line_count))
                continue
            ary = line.split('=')
            variable = ary[0]
            if not variable.endswith("$"):
                variable = variable + "$"
            if variable in my_oneofs:
                print("Duplicate one-of {} at line {}.".format(variable, line_count))
                continue
            value = '='.join(ary[1:])
            entries = value.split("\t")
            if len(entries) == 1:
                print("Need tabbed characters at line {}.".format(line_count))
                continue
            if entries[-1] not in oneof_keywords:
                print("Unrecognized ONEOF key at line {}: {}.".format(line_count, entries[-1]))
                continue
            this_oneof_type = oneof_keywords.index(entries[-1])
            my_oneofs[variable] = one_of(entries[:-1], this_oneof_type)
        elif line.startswith("P:"):
            line = line[2:].rstrip()
            for x in re.findall("\$[A-Za-z0-9]+\$", line):
                if x not in my_oneofs:
                    print("Unrecognized ONEOF keyword {} at line {}.".format(x, line_count))
                    continue
                line = line.replace(x, print_one_of(x), 1)
            print(line)
