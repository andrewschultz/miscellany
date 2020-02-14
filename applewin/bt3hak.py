# bt3hak.py
#
# a utility to hack Bard's Tale 3 save states or to read important information from them
#
# currently editing allows
# --warping to a different place on the level
#
# current information that can be derived
# --x/y coordinates of current level
# --code wheel reading to type in to world-jump (must be mid-spell)

import re
import sys
from mytools import latest_of

def usage():
    print("===================editing commands")
    print("c= / xy= / yx= tells (decimal) to change coordinates to")
    print("f= changes file name")
    print("i= adds item list")
    print("===================informational commands")
    print("cg or gc gets the coordinates in the current dungeon, W and N of the SE corner")
    print("cw gives code wheel reading")
    exit()

def byte_array_to_file(my_ary, my_file_name):
    try:
        f = open(file_name, "wb")
    except:
        print("Failed to open", file_name)
    try:
        f.write(my_ary)
    except:
        print("Failed to write to", file_name)
    f.close()

def file_to_byte_array(file_name):
    try:
        f = open(file_name, "rb")
    except:
        sys.exit("Can't find {}".format(file_name))
    ba = bytearray(f.read())
    f.close()
    return ba

def add_items(my_items):
    l = len(my_items)
    bain = file_to_byte_array(file_name)
    for x in range(0, 7):
        if not my_items: break
        for y in range(0, 12):
            my_offset = 0x470 + 0x30 + x * 0x80 + y * 0x3 + 1
            if bain[my_offset]:
                continue
            bain[my_offset] = my_items[0]
            bain[my_offset+1] = 0xff
            print("Gave item", hex(my_items[0]), "to character", x+1)
            my_items = my_items[1:]
            if not my_items:
                print("Placed all", l, "items. Yay!")
                break
    if l == len(my_items):
        print("All inventories full. Replaced nothing.")
    elif len(my_items) != 0:
        print("Placed", l - len(my_items), "of", l, "items.")
    byte_array_to_file(bain, file_name)
    sys.exit()

def extract_code_wheel():
    try:
        f = open(file_name, "rb")
    except:
        sys.exit("Can't find {}".format(file_name))
    b = bytearray(f.read())
    f.close()
    wheel_data = b[0xaa5a:0xaa60]
    wheel_start = int(b[0xaa61])
    wheel_code = ''.join([str(x - 0xb0) for x in wheel_data[wheel_start:]])
    print("Wheel code:", wheel_code)
    
def get_coords():
    b = file_to_byte_array(file_name)
    print("X={} Y={}".format(b[0x7a], b[0x79]))
    exit()

def change_coords(coord_string):
    b = file_to_byte_array(file_name)
    carg = coord_string.split(",")
    try:
        b[0x7a] = int(carg[0])
        b[0x79] = int(carg[1])
    except:
        sys.exit("Need two integers as parameters, x- and y-coordinates.")
    byte_array_to_file(b, file_name)
    print("Changed to {}, {}".format(carg[0], carg[1]))
    return

# you'll want to change this
file_name = latest_of(["bt3_boot.aws", "bt3_dungeon_a.aws", "bt3_dungeon_b.aws"])
#file_name = "bt3_dungeon_b.aws"

print("Default file name =", file_name)

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg[:2] == 'f=':
        file_name = arg[2:]
    elif arg[:2] == 'c=':
        change_coords(arg[2:])
    elif arg[:2] == 'cg' or arg[:2] == 'gc':
        get_coords()
    elif arg[:3] == 'xy=' or arg[:3] == 'yx':
        change_coords(arg[3:])
    elif arg[:3] == 'b':
        file_name = "bt3_dungeon_b.aws"
    elif arg[:3] == 'a':
        file_name = "bt3_dungeon_a.aws"
    elif re.search("^[0-9]+,[0-9]+$", arg):
        change_coords(arg)
    elif arg[:2] == 'i=':
        try:
            item_list = [int(x, 16) for x in arg[2:].split(",")]
        except:
            print("Bad item list. I need hexadecimal numbers.")
            sys.exit()
        add_items(item_list)
        exit()
    elif arg == 'cw':
        extract_code_wheel()
        exit()
    else:
        usage()
    cmd_count += 1
