import glob
import sys
import re
import base64

file_array = []

png_only = True

try:
	file_tries = sys.argv[1:]
except:
	sys.exit("Need file name.")

for f in file_tries:
    if len(f) == 1:
        sys.stderr.write("IGNORING likely flag {}.\n".format(f))
        continue
    if '*' in f:
        g = glob.glob(f)
        if png_only:
            g = [x for x in g if x.lower().endswith('.png')]
        file_array.extend(g)
    else:
        file_array.append(f)

if not len(file_array):
    sys.stderr.write("No files were found!\n")
    sys.exit()

sys.stderr.write("{} file{} to process.\n".format(len(file_array), 's' if len(file_array) > 1 else ''))
sys.stderr.flush()

for file_name in file_array:
    try:
        file = open(file_name, 'rb')
    except:
        sys.stderr.write("No file {}.\n".format(file_name))
        continue
    file_content = file.read()
    file_mod = file_name.replace('-', '_')
    file_mod = file_mod.split('.')[0]

    #base64_one = base64.encodestring(file_content)
    base64_two = base64.b64encode(file_content)

    #print(base64_one)

    print('      {} : base64_png "{}" ;'.format(file_mod, base64_two.decode('ascii')))
