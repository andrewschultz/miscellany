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

def parselead(x):
    temp = re.split('-', x)
    if len(temp) == 1:
        return int(temp[0])
    try:
        diff = int(temp[0]) - int(temp[1])
        if diff < 0:
            diff = 0 - diff
        return diff
    except:
        print "you need a score difference, or a score like 80-60."
        exit()
        return 0

parser = argparse.ArgumentParser()

parser.add_argument("lead", type=str, help="team's lead")
parser.add_argument("time", type=str, help="time left (can use colon/period to delimit minutes)")

args = parser.parse_args()

lead = parselead(args.lead)

timeint = timesplit(args.time)

def floatTime(x):
    return (float(x) - 3.5) ** 2

def leadPct(x, y, z):
    retval = (floatTime(x+z))
    if x < 4:
        return 0
    return float(retval * 100) / float(y)

if args.lead < 4:
    print "Lead is too small to matter."
else:
    print("%.2f %% safe with ball" % leadPct(lead, timeint, 1))
    print("%.2f %% safe without ball" % leadPct(lead, timeint, 0))
    print("%2d:%02d cutoff time for with the ball" % (floatTime(lead+1) / 60, floatTime(lead+1) % 60))
    print("%2d:%02d cutoff time for without the ball" % (floatTime(lead) / 60, floatTime(lead) % 60))
