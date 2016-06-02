import sys
import re
import os.path

if len(sys.argv) < 3:
    print 'You need an input file and an output file.';
    sys.exit();

infile = sys.argv[1];
outfile = sys.argv[2];

if os.path.isfile(infile) == 0:
    print infile, 'doesn\'t exist.';
    sys.exit();

f1 = open(outfile, 'w');

with open(infile) as f:
    for line in f:
        if re.search("room id=", line):
            line2 = re.sub('.*name=\"', '', line);
            line2 = re.sub('\".*', '', line2);
            f1.write(line2);