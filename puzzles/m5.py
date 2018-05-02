with open("m5.txt") as file:
	for line in file:
		areas = line.lower().strip().split(",")
		sum = int(areas[-1])
		areas = sorted(int(x) for x in areas[:-1])

j = len(areas)
count = 0

for i in range (0, j):
	for i2 in range(i, j):
		for i3 in range(i2, j):
			for i4 in range(i3, j):
				if areas[i] + areas[i2] + areas[i3] + areas[i4] == sum:
					count = count + 1
					print(count, ":", areas[i], "+", areas[i2], "+", areas[i3], "+", areas[i4], "=", sum)
