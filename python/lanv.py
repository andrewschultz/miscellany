# lanv.py
#
# sorts out the cases of the i6 languageverb function
#
# usage: (no arguments yet, just looks at story.ni)

import i7

c = 0

lasts = [ '' ] * 6
cur_nfr = 0
cur_lev = 0

with open("story.ni") as file:
    for (line_count, line) in enumerate(file, 1):
        inl = i7.new_lev(line)
        if inl:
            # print('before', line.strip(), cur_lev, cur_nfr)
            # print(line_count, line.strip())
            cur_lev = inl
            nfr = 'not for release' in line.lower()
            if nfr: cur_nfr = (cur_lev if cur_lev > cur_nfr else cur_nfr)
            elif cur_lev >= cur_nfr: cur_nfr = 0
            for x in range(0, cur_lev): lasts[x] = ''
            lasts[cur_lev - 1] = line.strip()
            outline_str = '/'.join(lasts[cur_lev - 1:])
            # print('after', line.strip(), cur_lev, cur_nfr)
        if cur_lev > cur_nfr:
            if line.startswith("understand") and 'as something new' in line:
                c += 1
                print(cur_lev, cur_nfr, c, outline_str, line_count, line.strip())
                continue
