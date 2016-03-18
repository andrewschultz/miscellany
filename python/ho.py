import sys;
import re;

numString = ''

if len(sys.argv) > 1:
	if sys.argv[1] is 'i':
		numString = "#"

#f = open('c:/windows/system32/drivers/etc/hosts', 'r');
g = open('c:/coding/python/hosts', 'w');

with open('c:/windows/system32/drivers/etc/hosts') as f:
	for line in f:
		p = re.match('^#?127.0.0.1', line, 0);
		if p:
			line.replace("#", "");
			print (numString + line, file=g, end='');
		else:
			print (line, file=g, end='');


#if (p.match(q))