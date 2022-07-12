#
# rotrot.py: this takes a text file and goes through the Caesar Ciphers from 1 to 25.
#

import glob
import os
from string import ascii_uppercase
from string import ascii_lowercase

def rotate_string(original_string, shift_by):
    shift_by %= 26
    return_string = ''
    for x in original_string:
        if x.lower() in ascii_lowercase:
            high_bits = ord(x) & 0x60
            low_bits = ord(x) & 0x1f
            low_bits += shift_by
            if low_bits > 26:
                low_bits -= 26
            return_string += chr(high_bits + low_bits)
        else:
            return_string += x
    return return_string

rotate_delta = 1

def convert_prerot(file_name):
    current_rotate = 0
    am_rotating = False
    am_writing = False
    ever_wrote = False
    with open(file_name) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("FILE="):
                file_to_write = line[5:].strip()
                f = open(file_to_write, "w")
                ever_wrote = True
                am_writing = True
                continue
            if line.lower().startswith("==start-rotate"):
                am_rotating = True
                continue
            if line.lower().startswith("==end-rotate"):
                am_rotating = False
                continue
            if am_writing:
                if not am_rotating or not line.strip():
                    f.write(line)
                    continue
                current_rotate += rotate_delta
                if current_rotate > 26:
                    current_rotate -= 26
                f.write(rotate_string(line, current_rotate))
        f.close()
        if not ever_wrote:
            print("No FILE= command in the pre-file, so I don't know where to write to.")
            return
        os.system(file_to_write)

my_glob = glob.glob("prerot*")

if len(my_glob) == 0:
    sys.exit("You need a prerot-walkthrough file in this directory.")

for f in my_glob:
    convert_prerot(f)

