###########################################################
#bj.py
#
#using argparse to get the Bill James safe lead coefficient
#

import re
import sys
import argparse

def timesplit(x):
	temp = re.split('[:.]', x)
	if len(temp) > 2:
		exit()
	retval = int(temp[0])
	if len(temp) == 2:
		retval = retval * 60;
		retval = retval + int(temp[1])
	return retval


parser = argparse.ArgumentParser()

parser.add_argument("lead", type=int, help="team's lead")
parser.add_argument("time", type=str, help="time left (can use colon/period to delimit minutes)")

args = parser.parse_args()

timeint = timesplit(args.time)

def floatTime(x):
    return (float(x) - 3.5) ** 2

def lead(x, y, z):
    retval = (floatTime(x+z))
    if x < 4:
        return 0
    return float(retval * 100) / float(y)

if args.lead < 4:
    print "Lead is too small to matter."
else:
    print("%.2f %% safe with ball" % lead(args.lead, timeint, 1))
    print("%.2f %% safe without ball" % lead(args.lead, timeint, 0))
    print("%2d:%02d cutoff time for with the ball" % (floatTime(args.lead+1) / 60, floatTime(args.lead+1) % 60))
    print("%2d:%02d cutoff time for without the ball" % (floatTime(args.lead) / 60, floatTime(args.lead) % 60))
