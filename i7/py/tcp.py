#
#tcp.py: transcript from youtube cut/paste from page
#

import os
import re
import pyperclip

temp_file = "c:\\writing\\temp\\from_webpage_transcript.txt"

max_width = 100

x = pyperclip.paste()
ary = x.split("\r\n")

def spacing_stuff(word_array, our_max_width):
    this_line = ''
    big_string = ''
    for w in word_array:
        if not len(this_line):
            this_line = w
        else:
            if len(this_line) + len(w) < our_max_width:
                this_line += " " + w
            else:
                big_string += this_line + "\n"
                this_line = w
    if this_line:
        big_string += this_line
    return big_string

def is_time_marker(my_string):
    x = my_string.strip()
    return re.search("[0-9]+:[0-9]+", x)

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

copy_string = spacing_stuff(copy_string_array, max_width)

if to_file:
    f = open(temp_file, "w")
    f.write(copy_string)
    f.close()
    os.system(temp_file)
else:
    print(copy_string)
