open(A, "story.ni");

$spc{"volume"} = 0;
$spc{"book"} = 2;
$spc{"part"} = 4;
$spc{"chapter"} = 6;
$spc{"section"} = 8;

while ($a = <A>)
{
  $line++;
  if ($a =~ /^(book|chapter|part|volume|section) /i)
  {
    chomp($a);
	$ash = $a; $ash =~ s/ .*//g;
    $b = $a; $b =~ s/ .*//g; $c = " " x $spc{$b}; #print "$spc{$b} spaces for $b.\n";
	$inc{lc($ash)}++;
    print "$c$a ($line)\n"; }
}

for $x (sort keys %inc) { print "$inc{$x} of $x.\n"; $total += $inc{$x}; }

print "$total total breaks.\n";

close(A);
