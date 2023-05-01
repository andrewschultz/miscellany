import os
import re
import pyperclip

temp_file = "c:\\writing\\temp\\from_webpage_transcript.txt"
x = pyperclip.paste()
ary = x.split("\r\n")

def is_time_marker(my_string):
    x = my_string.strip()
    return re.search("[0-9]+:[0-9]+", x)

transcript_next = False
to_file = True

copy_string = ""
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
        copy_string += a + "\n"
        continue

if to_file:
    f = open(temp_file, "w")
    f.write(copy_string)
    f.close()
    os.system(temp_file)
else:
    print(copy_string)
