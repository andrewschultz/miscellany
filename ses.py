import mytools as mt

from collections import defaultdict
import xml.etree.ElementTree as ET

slink = defaultdict(list)
file_name = mt.np_xml

news = 0
e = ET.parse(file_name)
root = e.getroot()
github_warnings = 0
link_warnings = 0
for elem in e.iter('File'):
    t = elem.get('filename')
    if t.startswith('new '):
        news += 1
        continue
    q = mt.follow_link(t).lower()
    if "users\\andrew\\documents\\github\\" in q and q.count("\\") >= 6:
        github_warnings += 1
        print("GH WARNING {} github file should be in non-github directory: {}".format(github_warnings, q))
    if q in slink:
        link_warnings += 1
        print("LINK WARNING: {} file and symbolic link both in notepad:".format(link_warnings))
        print(t, '=>', q)
    slink[q].append(t.lower())
    #print(elem.get('filename'))

print(github_warnings, "github warnings", link_warnings, "link warnings", news, "new files")
