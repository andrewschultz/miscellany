import sys
import glob
from PIL import Image
import mytools as mt

overwrite = False

file_names = []

red_t = green_t = blue_t = 255

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg.startswith("#"):
        if len(arg) != 7:
            sys.exit("Need a 6 digit hex number.")
        try:
            red_t = int(arg[1:3], 16)
            green_t = int(arg[3:5], 16)
            blue_t = int(arg[5:7], 16)
            print("Got transparency number.")
        except:
            sys.exit("Bad hex value {}.".format(arg[1:]))
    elif '*' in arg:
        file_names.extend(glob.glob(arg))
    elif arg == 'o':
        overwrite = True
    else:
        if '.' not in arg:
            arg += '.png'
        file_names.append(arg)
    cmd_count += 1

if not len(file_names):
    print("Need a file name or names.")

for file_name in file_names:
    img = Image.open(file_name)
    rgba = img.convert("RGBA")
    datas = rgba.getdata()

    newData = []
    for item in datas:
        if item[0] == red_t and item[1] == green_t and item[2] == blue_t:  # finding transparency color (default = white) by its RGB value
            # storing a transparent value when we find a black colour
            newData.append((red_t, green_t, blue_t, 0))
        else:
            newData.append(item)  # other colours remain unchanged

    rgba.putdata(newData)

    if file_name.endswith('.bmp'):
        file_name = file_name[:-4] + ".png"
        mt.warn("Replacing BMP extension with PNG")
    if overwrite:
        file_out = file_name
    elif '\\' in file_name or '/' in file_name:
        file_out = file_name.replace('.', '-t.')
    else:
        file_out = 'tra-' + file_name
    rgba.save(file_out, "PNG")
    print("Wrote out to", file_out)
    if not overwrite:
        print("Remember, -o/o overwrites.")
