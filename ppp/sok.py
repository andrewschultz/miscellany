####################################################
#sok.py
#usage sok.py [udhv]+
#
#sok.txt is the text file. It has lines like 2U 4L 3D 5R.
#

import re
import sys

dir_array = ['U','R','D','L'];
ord_array = [0, 1, 2, 3];

rotate = 0;
horiz = 0;

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
	ord_array = ord_array[rotate:4] + ord_array[0:rotate]
	if horiz == 1:
		ord_array[3], ord_array[1] = ord_array[1], ord_array[3];
	print ord_array, 'rotate', rotate, 'horiz', horiz;


def sokrepl (match):
    for q in range(0,4):
        if match.group(2).upper() == dir_array[q]:
            return match.group(1) + dir_array[ord_array[q]]
    return 'X'

infile = "sok.txt";

q = re.compile(r'(\b|[0-9\*]+)([ULDRuldr])\b')

with open(infile) as f:
	for line in f:
		print line;
		x = q.sub(sokrepl, line);
		print x;
