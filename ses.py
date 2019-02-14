#from pandas.plotting import register_matplotlib_converters
#register_matplotlib_converters()

import os
import datetime
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates

times = []
fitabs = []
newtabs = []

with open("c:/writing/scripts/ses.txt") as dat:
    for (line_count, line) in enumerate(dat, 1):
        if 'total files' not in line and 'new files' not in line: continue
        q = re.split('[:,] ', line.strip())
        fitabs.append(int(re.sub(" .*", "", q[1])))
        newtabs.append(int(re.sub(" .*", "", q[2])))
        tt = datetime.datetime.strptime(q[0], "%Y-%m-%d %H:%M:%S")
        times.append(tt)

sumz = [x + y for x,y in zip(fitabs, newtabs)]
plt.plot_date(times, fitabs, xdate=True, markersize=1, color='g')
plt.plot_date(times, newtabs, xdate=True, markersize=1, color='#ff8000')
plt.plot_date(times, sumz, xdate=True, markersize=1, color='#808080')
#plt.plot(times[1:5], newtabs[1:5])

plt.xlabel('Date',fontsize=12, color="#00ff00")
plt.ylabel("tabs open", fontsize=12, color="#ff0000")

plt.legend()
plt.savefig('ses.png')
os.system("ses.png")