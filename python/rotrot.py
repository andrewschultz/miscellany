#
# rotrot.py: this takes a text file and goes through the Caesar Ciphers from 1 to 25.
#

from shutil import copy
from filecmp import cmp
import sys
import glob
import os
from string import ascii_uppercase
from string import ascii_lowercase
import mytools as mt

print_number_rotations = True
rotate_delta = 1
rotate_both = False
open_post = False

temp_out = "c:/writing/temp/rotrot-out-temp.txt"

def usage():
    print("Commands:")
    print("r# changes the delta. Multiples of 2 and 13 are not recommended.")
    print("rb lets you produce both rotated and non-rotated documents.")
    print("p and np/pn toggle printing number-rotations of each line. This option is on by default.")
    sys.exit()

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

def convert_prerot(file_name, this_delta = rotate_delta):
    print("Rotating", file_name, "by", this_delta)
    current_rotate = 0
    am_rotating = False
    am_writing = False
    ever_wrote = False
    rotate_only = False
    with open(file_name) as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("FILE="):
                file_to_write = line[5:].strip()
                if this_delta == 0:
                    file_to_write = file_to_write.replace(".", "-unrotated.")
                f = open(temp_out, "w")
                ever_wrote = True
                am_writing = True
                continue
            if line.lower().startswith("==start-rotate"):
                am_rotating = True
                continue
            if line.lower().startswith("==end-rotate"):
                am_rotating = False
                continue
            if line.lower().startswith("==rotate-only"):
                rotate_only = True
                continue
            if line.lower().startswith("==no-rotate-only"):
                rotate_only = False
                continue
            if rotate_only and this_delta == 0:
                continue
            if am_writing:
                if not am_rotating:
                    f.write(line)
                    continue
                if line.strip():
                    current_rotate += this_delta
                    if current_rotate >= 26:
                        current_rotate -= 25
                    if print_number_rotations and current_rotate:
                        f.write("{:02d}:".format(current_rotate))
                f.write(rotate_string(line, current_rotate))
        f.close()
        if not ever_wrote:
            print("No FILE= command in the pre-file, so I don't know where to write to.")
            return
        if os.path.exists(file_to_write) and cmp(temp_out, file_to_write):
            print("No changes in {}. Returning without opening/rewriting.".format(file_to_write))
            return
        copy(temp_out, file_to_write)
        if open_post:
            os.system(file_to_write)

cmd_count = 1

while cmd_count < len(sys.argv):
    (arg, num, valid) = mt.parameter_with_number(sys.argv[cmd_count])
    if arg == 'r':
        if valid:
            rotate_delta = num
    elif arg in ( 'b', 'br', 'rb' ):
        rotate_both = True
    elif arg == 'p':
        print_number_rotations = True
    elif arg in ( 'np', 'pn' ):
        print_number_rotations = False
    elif arg in ( 'op', 'po' ):
        open_post = True
    else:
        usage()
    cmd_count += 1

my_glob = glob.glob("prerot*")

if len(my_glob) == 0:
    sys.exit("You need a prerot-walkthrough file in this directory.")

if rotate_both and not rotate_delta:
    print("WARNING: you set rotate_delta to 0 and set rotate_both, but this would just output the unencrypted file twice.")

for f in my_glob:
    convert_prerot(f)
    if rotate_both and rotate_delta:
        convert_prerot(f, this_delta = 0)

if os.path.exists(temp_out):
    os.remove(temp_out)
