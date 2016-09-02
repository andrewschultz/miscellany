####################################################
#sok.py
#usage sok.py [udhv]+
#
#sok.txt is the text file. It has lines like 2U 4L 3D 5R.
#

from array import *
import re
import sys

dir_array = ['U','R','D','L'];
ord_array = dir_array;
ord_array = array('i', [0,1,2,3]);

rotate = 0;
horiz = 0;

print ord_array;

if (len(sys.argv) > 1):
	for dir in sys.argv[1]:
		ld = dir.lower();
		if ld == 'v':
			rotate = rotate + 2;
			horiz = 1 - horiz;
		elif ld == 'h':
			horiz = 1 - horiz;
		elif ld == 'r':
			rotate = rotate + 1 + 2 * horiz;
		elif ld == 'l':
			rotate = rotate + 3 + 2 * horiz;
		else:
			print 'Did not recognize', ld;
		print dir, ord_array, rotate, horiz;
	ord_array = ord_array[rotate:4] + ord_array[0:rotate]
	print ord_array, 'rotate', rotate, 'horiz', horiz;
	if horiz == 1:
		ord_array[3], ord_array[1] = ord_array[1], ord_array[3];
	print ord_array, 'rotate', rotate, 'horiz', horiz;


def sokrepl (match):
	for q in range(0,4):
		if match.group() == dir_array[q]:
			return dir_array[ord_array[q]];
	print match.group();
	return 'X';

infile = "sok.txt";

q = re.compile(r'[ULDRuldr]\b');

with open(infile) as f:
	for line in f:
		print line;
		x = q.sub(sokrepl, line);
		print x;
