####################################
#sec.pl
#
#this reads in the volumes down to the sections in an Inform 7 source file and prints them out as
#formatted text, with some minor additional stats.
#

initializeStuff();
getIgnoreStrings();
readOutline();
readMain();

##########################
#initializeStuff
#
#variables defined

sub initializeStuff
{
  $idx = 0;

  $ignoreString = "roi";

  $spc{"volume"} = 0;
  $spc{"book"} = 2;
  $spc{"part"} = 4;
  $spc{"chapter"} = 6;
  $spc{"section"} = 8;
}

##########################
#readOutline
#
#reads the outline of book chapter part volume section
sub readOutline
{
open(A, "story.ni") || die ("No story.ni in this directory.");

while ($a = <A>)
{
  $line++;
  if ($a =~ /^(book|chapter|part|volume|section) /i)
  {
    chomp($a);
	$ash = $a; $ash =~ s/ .*//g;
    $b = $a; $b =~ s/ .*//g; $c = " " x $spc{$b}; #print "$spc{$b} spaces for $b.\n";
	$inc{lc($ash)}++;
	@strs[$idx] = "$c$a ($line/";
	@lineNum[$idx] = $line;
	@depth[$idx] = $spc{$b} / 2;
	$idx++;
  }
}
}

##############################
#ReadMain
#the main function
#
sub readMain
{
for (0..$#strs)
{
  $foundYet = 0;
  for $j ($_+1..$#strs)
  {
    if (@depth[$j] <= @depth[$_]) { $temp = @lineNum[$j] - @lineNum[$_]; @strs[$_] .= "$temp)"; $foundYet = 1; last; }
	if ($j == $#strs) { @strs[$_] .= ($line - @lineNum[$_]) . ")"; }
  }
  if ($foundYet == 0) { @strs[$_] .= ($line - @lineNum[$_]) . ")"; }
}

$printable = 1;
for (0..$#strs)
{
  $temp = @strs[$_]; $t2 = $temp;
  $t2 =~ s/ \([0-9].*//g;
  if ($t2 =~ /^volume /)
  {
  if ($ig{$t2})
  {
    $ignores++;
    $printable = 0;
	#print "Ignoring $t2\n";
  }
  else { $printable = 1; $views++; }
  }
  if ($printable)
  {
  print @strs[$_] . "\n";
  }
  }

close(A);

for $x (sort keys %inc) { print "$inc{$x} of $x.\n"; $total += $inc{$x}; }

print "$total total breaks.\n";

if ($ignores) { print "$ignores volumes ignored, $views read.\n"; }
}

#################################
#getIgnoreStrings
#finds the ignore strings a=b,c,d in sec-i.txt
#
sub getIgnoreStrings
{
open(A, "c:/writing/scripts/sec-i.txt");
while ($a = <A>)
{
  chomp($a); @b = split(/:/, $a);
  if (@b[0] eq $ignoreString)
  {
    @ignore = split(/,/, @b[1]);
    for (@ignore)
    {
      $ig{"volume $_"} = 1;
	}
  }
}
close(A);
}
