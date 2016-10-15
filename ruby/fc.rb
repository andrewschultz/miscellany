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

def moverows(from, to)
	if $y[from].length == 0
		return 0
	end
	if canPut($y[from][$y[from].length-1], $y[to][$y[to].length-1]) == 1
		$y[to].push($y[from].pop())
		printcards()
	else
		puts "Can't move from " + from.to_s + " to " + to.to_s
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
	moverows(e[0].to_i, e[1].to_i)
  end
end

