$zup = "c:/writing/scripts/zup.txt";
open(A, $zup) || die ("$zup not available, bailing.");

while ($count <= $#ARGV)
{
  if ($count =~ /,/)
  {
    @commas = split(/,/, $count);
	for (@commas) { $here{$_} = 1; }
  }
  else
  {
  $here{@ARGV[$count]} = 1;
  }
  $count++;
}

$count = 0;

while ($a = <A>)
{
  chomp($a);

  #print "$a: ";

  if ($a =~ /^name=/i)
  {
    $a =~ s/^name=//gi;
    @b = split(/,/, $a);
	for $idx(@b)
	{
	  print "$idx\n";
	  if ($here{$idx}==1)
	  {
	    $triedSomething = 1;
	    $zipUp = 1;
	    $zipcmd = "7z a";
	  }
	}
  }
  if ($a =~ /^;/) { last; }
  if (!$zipUp) { next; }

  for ($a)
  {

  /^!/ && do { processCmd($zipcmd); $zipUp = 0; next; };
  /^out=/ && do { $a =~ s/^out=//g; $zipcmd .= " \"c:\\games\\inform\\zip\\$a\""; next; };
  /^>>/ && do { $cmd = $a; $cmd =~ s/^>>//g; `$cmd`; print "Running $cmd\n"; next; };
  /^>/ && do { $fileName = $a; $fileName =~ s/^>//g; $zipcmd = "$zipcmd "; $needFile = 1; next; };
  /^F=/i && do
  {
    $a =~ s/^F=//gi;
    #$fileName =~ s/\./_release_$a\./g;
    $needFile = 0;
	if ((! -f "$a") && (! -d "$a") && ($a !~ /\*/)) { print "No file/directory $a.\n"; }
	else
	{
    $zipcmd .= " \"$a\"";
	}
	#print "Add $a, **$zipcmd\n";
    next;
  };
  /^c:/ && do
  {
    $cmd .= " \"$a\"";
    if ((! -f "$a") && (! -d "$a")) { print "WARNING: $a doesn't exist.\n"; }
    next;
  };
  /^;/ && do { last; next; };
  }
  #print "Cur cmd $cmd\n";
}

close(A);

if (!$triedSomething) { print "Didn't find anything in @ARGV.\n"; }

sub processCmd
{
  print "$_[0]\n";
  `$_[0]`;
}