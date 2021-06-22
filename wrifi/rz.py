# rz.py: grabs text from rhymezone

import re
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
from mytools import npo

rz_out = "c:/writing/temp/rz-out.txt"

try:
    my_word = sys.argv[1]
    url = "https://rhymezone.com/r/rhyme.cgi?Word={}&typeofrhyme=perfect&org1=syl&org2=l&org3=y".format(my_word)
except:
    sys.exit("I need a word to rhyme.")

html = urlopen(url).read()
soup = BeautifulSoup(html, features="html.parser")

# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()    # rip it out

# get text
text = soup.get_text()

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines

read_syllables = False
any_syllables = False
out_string = ''

for x in chunks:
    if re.search("^[0-9] syllable", x):
        read_syllables = True
        any_syllables = True
    if 'almost rhyme' in x.lower() or 'more ideas' in x.lower():
        read_syllables = False
    if 'words and phrases that' in x.lower():
        out_string += "\n" + x
    if read_syllables:
        if 'syllable' in x:
            out_string += "\n" + x
        else:
            out_string += x.replace(',', ', ')

if not any_syllables:
    sys.exit("Failed to read anything.")

out_string = '=========================Rhymes for {}=========================\n'.format(my_word) + out_string.lstrip()

f = open(rz_out, "w")
f.write(out_string.strip())
f.close()
npo(rz_out)