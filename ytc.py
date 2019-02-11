#
#
# ytc.py : youtube caption downloader
#
#

import system
import os
from youtube_transcript_api import YouTubeTranscriptApi

video_id = "https://www.youtube.com/watch?v=gcH6tFugYfo"

def usage():
	print("So far the only option is the youtube id.")
	exit()

print_output = False
write_output = True
launch_output = True

line_string = ""
trans_file = "c:/coding/perl/proj/ytrans.txt"

length_of_line = 0

max_line = 150

count = 0

while count < len(sys.argv):
	arg = sys.argv[count]
	if arg[0] == '-': arg = arg[1:]
	if arg.lower().startswith('http') or re.search(r'[0-9a-zA-Z]{6}', arg):
		video_id = re.sub("=", "", arg)
	else:
		usage()
	count += 1

video_id = re.sub(".*=", "", video_id)

q = YouTubeTranscriptApi.get_transcript(video_id)

if not video_id: sys.exit("Specify video id.")
if not (print_output or write_output): sys.exit("Need to specify print or write output on. To launch, just use -jl.")

for q0 in q:
	a = q0['text']
	if not a.strip():
		line_string += "\n"
		length_of_line = 0
	if len(a) + length_of_line >= max_line and length_of_line > 0:
		line_string += "\n" + a
		length_of_line = len(a)
	else:
		line_string += " " + a
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
