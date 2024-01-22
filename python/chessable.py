import sys
import os
import pendulum

out_file = "chessable.htm"

def any_updates():
	return True

if not any_updates():
	sys.exit("No updates or override detected. Exiting.")

out_string = "<html>\n<title>Chessable goal stuff</title>\n<body>\n<center>\n<table border=1>\n"

with open("chessable.txt") as file:
	for (line_count, line) in enumerate (file, 1):
		if line.startswith("HEADER"):
			continue
		if line.startswith("#"):
			continue
		if line.startswith(';'):
			break
		a = line.strip().split(',')
		first_link = f'<a href="{a[0]}">{a[1]}</a>'
		b = [first_link]
		b.extend(a[2:])
		my_str = "<tr><td>" + "</td><td>".join(b) + "</td></tr>\n"
		out_string += (my_str)

out_string += "</table>\n</center>\n</body>\n</html>"

f = open(out_file, "w")
f.write(out_string)
f.close()

os.system(out_file)