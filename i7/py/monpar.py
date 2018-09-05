
from difflib import Differ
import sys
import re

file_name = sys.argv[1]

last_test_text = []
cur_test_text = []

in_test_text = False

d = Differ()

with open(file_name) as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith(">"):
            if not last_test_text and not cur_test_text:
                print(line.strip(), "(no test text before)")
                continue
            if not cur_test_text:
                print(line.strip(), "No current test. Maybe this is a test command or an out of world action.")
                continue
            elif cur_test_text == last_test_text:
                print("No change in test text.")
            else:
                print("Changed text.")
                print("\n".join([x.strip() for x in list(d.compare(last_test_text, cur_test_text)) if re.search("^[\+\?-]", x)]))
            last_test_text = list(cur_test_text)
            cur_test_text = []
            print(line.strip())
        if "=START TESTS" in line:
            in_test_text = True
            continue
        if "=END TESTS" in line:
            in_test_text = False
            continue
        if in_test_text: cur_test_text.append(line)

