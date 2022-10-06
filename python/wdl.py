# wdl.py: wordle solver

import sys
from collections import defaultdict
from string import ascii_lowercase
from string import ascii_uppercase

wordle = defaultdict(bool)
words = defaultdict(bool)

cond_match_global = []
negative_letters_global = ''

def get_let_freq(word_array):
    word_freq = defaultdict(int)
    let_freq = defaultdict(int)
    for a in ascii_lowercase:
        for w in word_array:
            word_freq[a] += a in w
            let_freq[a] += w.count(a)
    return (word_freq, let_freq)

def print_best_remaining(my_lets, word_freq, local_word_dict = words, show_total_poss = False, header_string = 'Results of Print-Best-Remaining', known_letters = ''):
    let_left = defaultdict(int)
    word_tuple = defaultdict(int)
    for w in local_word_dict:
        let_left[w] = sum([l in my_lets for l in set(w) if l not in known_letters])
        word_tuple[w] = (let_left[w], sum([word_freq[l] for l in set(w) if l in w and l not in known_letters]))
    count = 0
    output_string = header_string + ' (letters unguessed, letters eliminated)'
    for x in sorted(word_tuple, key=lambda x: word_tuple[x][::-1], reverse=True):
        if count == 20:
            print(output_string.strip())
            extra_string = ", total word possibilities = {}".format(len(word_tuple))
            print("Got max{} so cutting off printing.".format(extra_string if show_total_poss else ''))
            return
        if count % 5 == 0:
            output_string += "\n"
        else:
            output_string += ' / '
        count += 1
        output_string += "{} {} {}".format(count, x.upper() if x in wordle else x, word_tuple[x])
    print(output_string.strip())
    if count > 1:
        print("All", len(word_tuple), "possibilities listed above.")
    elif count == 1:
        print("ONLY POSSIBILITY LISTED ABOVE!")
    else:
        print("No matches were found.")

def is_poss_match(my_word, cond_match, negative_letters):
    for x in negative_letters_global + negative_letters:
        if x in my_word:
            return False
    for w in cond_match_global + cond_match:
        for x in range(0, 5):
            if w[x] == '.':
                continue
            if w[x] in ascii_uppercase:
                if my_word[x] != w[x].lower():
                    return False
            if w[x] in ascii_lowercase:
                if my_word[x] == w[x] or w[x] not in my_word:
                    return False
    return True

def subsumed(a1, a2):
    if len(a1) != len(a2):
        return False
    for y in range(0, len(a2)):
        if a1[y] != a2[y] and a1[y] != '.':
            return False
    return True

def smart_append(my_array, my_new_string):
    ret_array = []
    for m in my_array:
        if subsumed(m, my_new_string):
            continue
        ret_array.append(m)
    ret_array.append(my_new_string)
    return ret_array

def process_input(my_input):
    global cond_match_global
    global negative_letters_global
    negative_letters = ''
    cond_match = []
    bad_string = False
    match_only_unique = False
    this_global = False
    if my_input.startswith('/'):
        this_global = True
        my_input = my_input[1:]
    if my_input.startswith('?'):
        print("Global clues so far:")
        for x in cond_match_global:
            print("  " + x)
    if my_input.startswith("\\"):
        cond_match_global = []
        negative_letters_global = ''
        my_input = my_input[1:]
    for y in my_input.strip().split(' '):
        if y.startswith('-'):
            if this_global:
                negative_letters_global += y[1:]
            else:
                negative_letters += y[1:]
        elif len(y) == 5:
            if this_global:
                cond_match_global = smart_append(cond_match_global, y)
            else:
                cond_match = smart_append(cond_match, y)
        elif y == 'u':
            match_only_unique = True
        else:
            print("Bad string", y)
            bad_string = True
    known_letters = []
    for cm in cond_match + cond_match_global:
        known_letters.extend([ x.lower() for x in cm if x.lower() in ascii_lowercase ])
    if bad_string:
        return
    in_word = [x for x in ''.join(cond_match).lower() if x in ascii_lowercase]
    count = 0
    poss_words = []
    to_add = []
    for y in words:
        if match_only_unique:
            if len(set(y)) != len(y):
                continue
        if is_poss_match(y, cond_match, negative_letters):
            count += 1
            poss_words.append(y)
            to_add.append(y)
    if not count:
        print("No matches found for that guess set.")
        return
    my_lets = [let for let in ascii_lowercase if let not in my_input.lower()]
    (word_freq, let_freq) = get_let_freq(poss_words)
    for w in sorted(word_freq, key=word_freq.get):
        if word_freq[w]:
            print(('===> ' + w.upper() if w in in_word else w), let_freq[w], word_freq[w])
    print_best_remaining(my_lets, word_freq, to_add, show_total_poss = True, known_letters = known_letters, header_string = 'Guesses with all known letters')
    print_best_remaining(my_lets, word_freq, known_letters = known_letters, header_string = 'Best guesses to eliminate words')

with open("c:/writing/dict/wordle.txt") as file:
    for (line_count, line) in enumerate (file, 1):
        for x in line.lower().strip().split(' '):
            wordle[x] = True

with open("c:/writing/dict/words-5.txt") as file:
    for (line_count, line) in enumerate (file, 1):
        words[line.lower().strip()] = True

if len(sys.argv) > 1:
    process_input(' '.join(sys.argv[1:]))

while 1:
    my_input = input("Get stuff ->")
    if not my_input:
        sys.exit("Goodbye!")
    process_input(my_input)

