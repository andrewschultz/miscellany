from collections import defaultdict

def hunds(x):
    return (x % 1000) // 100

find_digit = defaultdict(bool)

count = 6

with open("m10.txt") as file:
    for line in file:
        find_digit.clear()
        nu = [float(x) for x in line.strip().split(',')]
        print(nu)
        num = int(nu[0] * 1000)
        div = int(nu[1] * 2)
        if len(nu) > 2:
            for x in nu[2:]:
                x2 = int(x)
                find_digit[x2] = True
        if div % 2 == 0: div = div // 2
        q = num % div
        num = num - q;
        print(count, ":", div, "========")
        no_keys = len(find_digit.keys()) == 0
        while num < int(nu[0]+1) * 1000:
            num = num + div
            if no_keys or hunds(num) in find_digit.keys(): print(num)
        count = count + 16