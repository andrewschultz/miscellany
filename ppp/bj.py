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

parser.add_argument("lead", type=str, help="team's lead")
parser.add_argument("time", type=str, help="time left (can use colon/period to delimit minutes)")

args = parser.parse_args()

timeint = timesplit(args.time)

def lead(x, y, z):
	retval = (float(x) - 3.5 + z) ** 2
	return retval * 100 / y
	
print lead(args.lead, timeint, 1), '% safe with ball'
print lead(args.lead, timeint, 0), '% safe with ball'

