#!/usr/bin/env ruby
############################
#fc.rb
#a script for playing FreeCell in ruby
#

def usage()
  puts "q = quit"
  puts "(1-8a-d)(1-8a-d) = move"
  puts "r = force foundation"
  puts "? = this"
end

$face=Array['A','2','3','4','5','6','7','8','9','10','J','Q','K']
$suit=Array['C','d','S','h']

$vertical = 1

def tocard(raw)
	mystr = $face[raw % 13]
	if raw % 13 != 9
		mystr = ' ' + mystr
	end
	mystr = mystr + $suit[raw/13]
	return mystr
end

def printcards()
	if $vertical
		printcardsV()
	else
		printcardsH()
	end
end

def printcardsH()
	for z in 1..8
		puts $y[z].map{|a| tocard(a)}.join(' ')
	end
end

def printcardsV()
	tryAgain = 1
	curLine = 0
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

ARGF.each_line do |e|
  if e.chomp == ""
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
  puts e
end

