#
#
# ytc.py : youtube caption downloader
#
# usage: ytc (id) (s/e/es/es)

import ytkey
import re
import sys
import os
from youtube_transcript_api import YouTubeTranscriptApi
import pyperclip

DEVELOPER_KEY = ytkey.my_dev_key()

video_id = ""
default_video_id = "https://www.youtube.com/watch?v=gcH6tFugYfo"

def usage():
    print("You can and should specify the youtube id.")
    print("-s/e/es/se lets you show start/end times.")
    print("-w specifies new line width, max={:d} min={:d}".format(min_max_line,max_max_line))
    exit()

def id_from_url(x):
    if 'youtu.be' in x:
        x = re.sub("^http(s)?://youtu.be/", "", x)
        x = re.sub("\?.*", "", x)
        return x
    x = re.sub(".*watch\?v=", "", x)
    x = re.sub("\&.*", "", x)
    return x

def trans_to_file(hlink, fi):
    length_of_line = 0
    ids = id_from_url(hlink)
    q = YouTubeTranscriptApi.get_transcript([ids])
    results = youtube.videos().list(id=ids, part='snippet').execute()
    for result in results.get('items', []):
        title = "Title: " + result['snippet']['title']
    line_string = "Transcript for YouTube video at https://www.youtube.com/watch?v={:s}\n\n{:s}\n\n".format(hlink, title)
    for q0 in q:
        a = q0['text']
        st = q0['start']
        en = q0['start'] + q0['duration']
        stm = int(st) // 60
        sts = st % 60
        enm = int(en) // 60
        ens = en % 60
        if flag_start and flag_end:
            a = "({:02d}:{:05.2f}-{:02d}:{:05.2f}) {:s}".format(stm, sts, enm, ens, a)
        elif flag_start:
            a = "({:05.2f}) {:s}".format(st, a)
        elif flag_end:
            a = "(-{:05.2f}) {:s}".format(en, a)
        if not a.strip():
            line_string += "\n"
            length_of_line = 0
        if len(a) + length_of_line >= max_line and length_of_line > 0:
            line_string += "\n" + a
            length_of_line = len(a)
        else:
            if length_of_line: line_string += " "
            line_string += a
            length_of_line += len(a) + 1
    print("Writing to", fi)
    f = open(fi, "w")
    f.write(line_string)
    f.close()

print_output = False
write_output = True
launch_output = True

flag_start = False
flag_end = False

trans_file = "c:/coding/perl/proj/ytrans.txt"

length_of_line = 0

max_line = 150
min_max_line = 90
max_max_line = 300

clipboard = False

count = 1

while count < len(sys.argv):
    arg = sys.argv[count]
    if arg[0] == '-': arg = arg[1:]
    if arg.lower().startswith('http') or re.search(r'[0-9a-zA-Z]{6}', arg): video_id = re.sub(".*=", "", arg)
    elif arg == 'se' or arg == 'es': flag_start = flag_end = True
    elif arg == 's': flag_start = True
    elif arg == 'e': flag_end = True
    elif arg == 'c': clipboard = True
    elif arg[0] == 'w':
        temp = int(arg[1:])
        if temp < min_max_line:
            print("Need max line of at least", min_max_line)
        elif temp > max_max_line:
            print("Need max line of at most", max_max_line)
        else:
            max_line = temp
    else: usage()
    count += 1

from apiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)

#https://www.youtube.com/watch?v=GFphNr0FK-0
if not video_id:
    if clipboard:
        cboard = pyperclip.paste()
        cblinks = cboard.split("\n")
        valid = 0
        for x in cblinks:
            print(x)
            if not x.startswith("http"): continue
            valid += 1
            tempfi = "ytrans-{:d}.txt".format(valid)
            trans_to_file(x, tempfi)
            os.system(tempfi)
        if not valid: sys.exit("No valid links found on clipboard.")
        sys.exit("{:d} youtube video{:s} to files.".format(valid, 's' if valid == 1 else ''))

video_id = re.sub(".*=", "", video_id)

ids = video_id
results = youtube.videos().list(id=ids, part='snippet').execute()

title = ""

for result in results.get('items', []):
    title = "Title: " + result['snippet']['title']

if not video_id: sys.exit("Specify video id or use -c for clipboard.")
if not (print_output or write_output): sys.exit("Need to specify print or write output on. To launch, just use -jl.")

q = YouTubeTranscriptApi.get_transcript(video_id)

line_string = "Transcript for YouTube video at https://www.youtube.com/watch?v={:s}\n\n{:s}\n\n".format(video_id, title)

for q0 in q:
    a = q0['text']
    st = q0['start']
    en = q0['start'] + q0['duration']
    stm = int(st) // 60
    sts = st % 60
    enm = int(en) // 60
    ens = en % 60
    if flag_start and flag_end:
        a = "({:02d}:{:05.2f}-{:02d}:{:05.2f}) {:s}".format(stm, sts, enm, ens, a)
    elif flag_start:
        a = "({:05.2f}) {:s}".format(st, a)
    elif flag_end:
        a = "(-{:05.2f}) {:s}".format(en, a)
    if not a.strip():
        line_string += "\n"
        length_of_line = 0
    if len(a) + length_of_line >= max_line and length_of_line > 0:
        line_string += "\n" + a
        length_of_line = len(a)
    else:
        if length_of_line: line_string += " "
        line_string += a
        length_of_line += len(a) + 1

if print_output:
    print(line_string)

if write_output:
    print("Writing to", trans_file)
    f = open(trans_file, "w")
    f.write(line_string)
    f.close()

if launch_output:
    print("Launching", trans_file)
    os.system(trans_file)
