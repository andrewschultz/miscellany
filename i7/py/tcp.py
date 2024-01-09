#
#tcp.py: transcript from youtube cut/paste from page
#

import os
import sys
import re
import pyperclip

temp_file = "c:\\writing\\temp\\from_webpage_transcript.txt"

max_width = 100
default_breaks_after = 7
assigned_max_width = 0
assigned_breaks_after = 0

x = pyperclip.paste()
ary = x.split("\r\n")

def spacing_stuff(word_array, our_max_width, our_breaks_after):
    this_line = ''
    big_string = ''
    break_counter = 0
    for w in word_array:
        if not len(this_line):
            this_line = w
        else:
            if len(this_line) + len(w) < our_max_width:
                this_line += " " + w
            else:
                big_string += this_line + "\n"
                break_counter += 1
                if break_counter == our_breaks_after:
                    break_counter = 0
                    big_string += "\n"
                this_line = w
    if this_line:
        big_string += this_line
    return big_string

def is_time_marker(my_string):
    x = my_string.strip()
    return re.search("[0-9]+:[0-9]+", x)

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg.isdigit():
        max_width = int(arg)
    elif (arg.replace('b', '').isdigit()):
        my_num = int(arg.replace('b', ''))
        if assigned_breaks_after:
            mt.warn("Reassigned max_width from {} to {}.".format(assigned_breaks_after, my_num))
        assigned_breaks_after = my_num
    elif (arg.replace('w', '').isdigit()):
        max_width = int(arg)
        print("TRIVIA: You don't need a w before or after a number to establish width. It is chosen by default.")
    else:
        sys.exit("Need a # for max_width or #b/b# for carriage returns before extra break.")
    cmd_count += 1

if not assigned_breaks_after:
    mt.warn("Going with default max-width of", default_breaks_after)
    assigned_breaks_after = default_breaks_after

transcript_next = False
to_file = True

copy_string_array = []
count = 0

for a in ary:
    count += 1
    a = a.strip()
    if is_time_marker(a):
        transcript_next = True
        continue
    if transcript_next:
        if a == 'Now playing':
            break
        transcript_next = False
        copy_string_array.extend(a.split(' '))
        continue

copy_string = spacing_stuff(copy_string_array, assigned_max_width, assigned_breaks_after)

if to_file:
    f = open(temp_file, "w")
    f.write(copy_string)
    f.close()
    os.system(temp_file)
else:
    print(copy_string)
