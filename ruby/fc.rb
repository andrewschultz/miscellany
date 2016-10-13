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

def tocard(raw)
	mystr = $face[raw % 13]
	mystr = mystr + $suit[raw/13]
	return mystr
end

def printcards()
	print y[1][0]
end

x=Array(0..51).shuffle

y=Array[[],[],[],[],[],[],[],[],[]]

for z in 0..51
	y[z%8+1][z/8] = x[z]
end

for z in 1..8
	puts y[z].map{|a| tocard(a)}.join(',')
end

ARGF.each_line do |e|
  if e.chomp == "q"
    exit
  end
  if e.chomp == ""
    printcards()
  end
  if e.chomp == "?"
    usage()
    next
  end
  puts e
end

