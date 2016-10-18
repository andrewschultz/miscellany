#!/usr/bin/env ruby
############################
#fc.rb
#a script for playing FreeCell in ruby
#

$onoff=Array['on', 'off']
$face=Array['A','2','3','4','5','6','7','8','9','10','J','Q','K']
$suit=Array['C','d','S','h']
$empty=Array[-1,-1,-1,-1]
$found=Array[0,0,0,0]

$vertical = 1

x=Array(0..51).shuffle

$y=Array[[],[],[],[],[],[],[],[],[]]

for z in 0..51
	$y[z%8+1][z/8] = x[z]
end

class String
  def digit?
    !!match(/^[[:digit:]]+$/)
  end
end

def foundable(mycard)
	if mycard == -1
		return 0
	end
	themod = mycard.to_i % 13
	thesuit = mycard.to_i / 13
	if themod <= $found[(thesuit+3)%4] + 1 and themod <= $found[(thesuit+1)%4] + 1 and themod == $found[thesuit]
		return 1
	end
	return 0
end

def updateFound()
	searchForFound = 1
	while searchForFound == 1
		searchForFound = 0
		for z in 1..8
			if $y[z].length > 0
				if foundable($y[z][$y[z].length-1]) != 0
					$found[$y[z][$y[z].length-1]/13] += 1
					$y[z].pop()
					searchForFound = 1
				end
			end
		end
		for z in 0..3
			if foundable($empty[z]) != 0
				$found[$empty[z]/13] += 1
				$empty[z] = -1
				searchForFound = 1
			end
		end
	end
	for z in 0..3
		if $found[z] != 13
			return 0
		end
	end
	return 1
end

def tocard(raw)
	if raw == -1
		return "---"
	end
	mystr = $face[raw % 13]
	if raw % 13 != 9
		mystr = ' ' + mystr
	end
	mystr = mystr + $suit[raw/13]
	return mystr
end

def printcards()
	if updateFound() == 1
		print "Won game."
		exit()
	end
	if $vertical == 1
		printcardsV()
	else
		printcardsH()
	end
	print "Foundation:"
	for z in [0, 2, 1, 3]
		if $found[z] == 0
			print " ---"
		else
			print " " + tocard($found[z] + z * 13 - 1)
		end
	end
	puts
	print "Empty spaces: "
	for z in 0..3
		if $empty[z] == -1
			print " ---"
		else
			print " " + tocard($empty[z])
		end
	end
	puts
end

def printcardsH()
	for z in 1..8
		puts z.to_s + ":" + $y[z].map{|a| tocard(a)}.join(' ')
	end
end

def printcardsV()
	tryAgain = 1
	curLine = 0
	for z in 1..8
		print " (" + z.to_s + ")"
	end
	puts
	while tryAgain == 1
		tryAgain = 0
		thisLine = ""
		for z in 1..8
			if $y[z].length <= curLine
				thisLine += "    "
			else
				thisLine += " " + tocard($y[z][curLine])
				tryAgain = 1
			end
		end
		if tryAgain == 1
			puts thisLine
		end
		curLine += 1
	end
end

def maxShift()
	base = 1
	for z in 0..3
		if $empty[z].to_i == -1
			base = base + 1
		end
	end
	for z in 1..8
		if $y[z].length == 0
			base = base * 2
		end
	end
	return base
end

def canPut(lower, higher)
	l1 = lower / 13
	l2 = higher / 13
	if (l1 + l2) & 1 == 0
		return 0
	end
	if (higher % 13) - (lower % 13) == 1
		return 1
	end
	return 0
end

def thischain(from)
	retval = 1
	fromIdx = $y[from].length - 1	
	while fromIdx > 0
		if canPut($y[from][fromIdx], $y[from][fromIdx - 1]) == 1
			fromIdx -= 1
			retval += 1
		else
			return retval
		end
	end
	return retval
end

def possShift(from, to)
	if $y[from].length == 0
		return 0
	end
	if $y[to].length == 0
		return thischain(from)
	end
	fromIdx = $y[from].length - 1
	toval = $y[to][$y[to].length-1]
	chainLength = 1
	stillProc = 1
	while stillProc
		stillProc = 0
		if canPut($y[from][fromIdx], toval) == 1
			return chainLength
		end
		if fromIdx == 0
			return 0
		elsif canPut($y[from][fromIdx], $y[from][fromIdx - 1]) == 1
			stillProc = 1
		else
			return 0
		end
		fromIdx = fromIdx - 1
		chainLength += 1
	end
	return 0
end

def moverows(from, to)
	if from == to
		return 0
	end
	if $y[from].length == 0
		return 0
	end
	temp = possShift(from, to)
	if temp == 0
		puts "Cards don't match."
		return 0
	end
	theShift = maxShift()
	if $y[to].length == 0
		theShift /= 2
	end
	if temp <= theShift
		$y[to].push(*$y[from].last(temp))
		$y[from].pop(temp)
		printcards()
		return 0
	end
	puts "Can't currently move from " + from.to_s + " to " + to.to_s + ". Not enough rowspace. Want " + temp.to_s + " have " + theShift.to_s
	return 0
end

def usage()
  puts "q = quit"
  puts "(1-8a-d)(1-8a-d) = move"
  puts "r = force foundation"
  puts "? = this"
end

printcards()

ARGF.each_line do |e|
  e = e.chomp
  if e == ""
    printcards()
	next
  end
  if e == "v"
    $vertical = 1 - $vertical
	puts "Vertical print is " + $onoff[$vertical]
	printcards()
    next
  end
  if e == "?"
    usage()
    next
  end
  if e == "q"
    exit
  end
  if e[0].digit? and e[1].digit?
	moverows(e[0].to_i, e[1].to_i)
  elsif e[0].digit? and e[1] <= "d" and e[1] >= "a"
	myc = e[0].to_i
	if myc < 1 or myc > 8
		puts "Between 1 and 8."
		next
	end
	if $y[myc].length == 0
		puts "Empty column."
		next
	end
	temp = e[1].ord - 97
	if $empty[temp] != -1
		puts "That's full."
		next
	end
	$empty[temp] = $y[myc][$y[myc].length-1]
	$y[myc].pop()
	printcards()
	next
  elsif e[1].digit? and e[0] <= "d" and e[0] >= "a"
	myc = e[1].to_i
	mye = e[0].ord - 97
	if myc < 1 or myc > 8
		puts "Between 1 and 8."
		next
	end
	if $empty[mye] == -1
		print "Nothing there"
		next
	end
	if $y[myc].length == 0 or canPut($empty[mye], $y[myc][$y[myc].length-1]) == 1
		$y[myc].push($empty[mye])
		$empty[mye] = -1
		printcards()
		next
	end
	print "Couldn't place that."
	next
  elsif e[0] == "r" or e[1] == "r"
	if e.length > 2
		puts "Length is " + e.length.to_s
		puts "!" + e[2] + "!"
		print "r needs only 1 other letter, 1-8 a-d."
		next
	end
	puts "Trying to move to foundation."
	e = e.sub! 'r', ''
	if e[0].digit?
		myc = e[0].to_i
		if $y[myc].length > 0 and foundable($y[myc][$y[myc].length-1]) > 0
			found[$y[myc]/13] += 1
			$y[myc].pop()
			printcards()
		end
	elsif e[0] <= 'd' and e[0] >= 'a'
		temp = e[0].ord - 97
		if $empty[temp] == -1
			puts "That's empty."
			next
		end
		if foundable($empty[temp]) > 0
			found[$empty[temp]/13] += 1
			$empty[temp] = -1
			printcards()
		end
	end
	puts "wrong text for r."
	next
  end
end

