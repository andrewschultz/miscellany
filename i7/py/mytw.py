import re
import os

def check_valid_path():
    if not os.path.exists("style.css"):
        sys.exit("No style.css found. Be sure you are releasing to parchment.")
    if not os.path.exists("play.html"):
        sys.exit("No play.html found. Be sure you are releasing to Parchment.")

def rewrite_css():
    in_gameport = ever_gameport = False
    f = open("style2.css", "w")
    with open("style.css") as file:
        for (line_count, line) in enumerate (file, 1):
            if line.startswith("#gameport"):
                in_gameport = True
                ever_gameport = True
            if not line.strip():
                in_gameport = False
            if in_gameport:
                if line.strip().startswith("bottom:"):
                    f.write("\tbottom: 1.4em;\n")
                    continue
                elif line.strip().startswith("left:"):
                    f.write("\tleft: 1em;\n")
                    continue
            f.write(line)
    f.close()
    if not ever_gameport:
        print("Didn't find #gameport in style.css.")
    else:
        print("Found #gameport in style.css.")

def rewrite_play():
    got_css = False
    f = open("play2.html", "w")
    with open("play.html") as file:
        for (line_count, line) in enumerate (file, 1):
            if re.search("<link.*style.css", line):
                got_css = True
                line = line.replace("style.css", "style2.css")
            f.write(line)
    f.close()
    if not got_css:
        print("Didn't change play.html to play2.html.")
    else:
        print("Changed play.html to play2.html.")

check_valid_path()
rewrite_css()
rewrite_play()
