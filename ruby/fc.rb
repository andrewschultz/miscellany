#!/usr/bin/env ruby
############################
#fc.rb
#a script for playing FreeCell in ruby
#

class String
  def digit?
    !!match(/^[[:digit:]]+$/)
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

def possShift(from, to)
	if $y[from].length == 0
		return 0
	fromIdx = $y[from].length - 1
	toval = $y[to][$y[to].length-1]
	chainLength = 2
	stillProc = 1
	while stillProc
		stillProc = 0
		if canPut($y[from][fromIdx], toval)
			return chainLength
		end
		if fromIdx == 0
			return 0
		end
		if canPut($y[from][fromIdx], toval)
			stillProc = 1
		end
		fromIdx = fromIdx - 1
	end
end

def moverows(from, to)
	return
	if from == to
		return 0
	end
	if $y[from].length == 0
		return 0
	end
	temp = possShift(from, to)
	if temp == 0
		puts "Cards don't match."
		return
	end
	if (temp <= maxShift() and $y[to].len > 0) or (temp <= maxShift() / 2)
		$y[to].push(*$y[from].last(temp))
		printcards()
		return
	end
	puts "Can't currently move from " + from.to_s + " to " + to.to_s + ". Not enough rows."
	end
end

def usage()
  puts "q = quit"
  puts "(1-8a-d)(1-8a-d) = move"
  puts "r = force foundation"
  puts "? = this"
end

onoff=Array['on', 'off']
$face=Array['A','2','3','4','5','6','7','8','9','10','J','Q','K']
$suit=Array['C','d','S','h']
$empty=Array[-1,-1,-1,-1]
$found=Array[0,0,0,0]

$vertical = 1

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
	if $vertical == 1
		printcardsV()
	else
		printcardsH()
	end
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

x=Array(0..51).shuffle

$y=Array[[],[],[],[],[],[],[],[],[]]

for z in 0..51
	$y[z%8+1][z/8] = x[z]
end

printcards()

ARGF.each_line do |e|
  if e.chomp == ""
    printcards()
	next
  end
  if e.chomp == "v"
    $vertical = 1 - $vertical
	puts "Vertical print is " + onoff[$vertical]
	printcards()
    next
  end
  if e.chomp == "?"
    usage()
    next
  end
  if e.chomp == "q"
    exit
  end
  if e[0].digit? and e[1].digit?
	#moverows(1,1)
	#moverows(e[0].to_i, e[1].to_i)
  elsif e[0].digit? and e[1] < "e" and e[1] >= "a"
	puts "Trying to move to spare."
  elsif e[0] == "r" or e[1] == "r"
	puts "Trying to move to spare."
  end
end

