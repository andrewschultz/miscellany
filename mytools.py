import os

def cheap_html(text_str, out_file = "c:/writing/temp/temp-htm.htm", title="HTML generated from text", launch = True):
	f = open(out_file, "w")
	f.write("<html>\n<title>{:s}</title>\n<body><\n><pre>\n{:s}\n</pre>\n</body>\n</html>\n".format(title, text_str))
	f.close()
	if launch: os.system(out_file)

def nohy(x):
    if x[0] == '-': x = x[1:]
    return x.lower()

def is_limerick(x):
    if x.count != 4: return False
    temp = re.sub(".* #", "", x)
    if len(temp) > 120 and len(temp) < 240: return True

def slash_to_limerick(x):
    temp = re.sub(" *\/ ", "\n", x)
    return ("====\n" + temp)
