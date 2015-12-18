
if (@ARGV[0] eq "-p")
{ readFile(@ARGV[1]); }
elsif (@ARGV[0] eq "-pd")
{ readFile("c:\\tech\\trizbort\\redact.txt"); }
else
{ readArray(@ARGV); }

sub readFile
{
  print "Trying file $_[0]\n";
  open(CMD, "$_[0]") || die ("Can't open $_[0]");

  while ($a = <CMD>)
  {
  chomp($a);
  readLine($a);
  }
}

sub readLine
{
  my @ary = split(/ /, $_[0]);
  readArray(@ary);
}

sub readArray
{
  my $count = 0;
  my $runThis = 0;
  if (!$keep) { undef(%redact); } else { $keep = 0; }
  
  while ($count <= $#_)
  {
    my $a = $_[$count];
	my $b = $_[$count+1];
    for ($a)
	{
	/-k/ && do { $keep = 1; $count++; next; };
	/-r/ && do { @redact = split(/,/, $b); for (@redact) { $redact{"$_"} = 1; } $count += 2; next; };
	/-f/ && do { $inFile = $b; $count += 2; $runThis = 1; next; };
	/-o/ && do { $outFile = $b; $count += 2; next; };
	print "$a ($count) unknown.\n";
	usage();
	}
  }
  if ($runThis)
  {
    if (!$outFile) { $outFile = $inFile; $outFile =~ s/\.trizbort/-redact\.trizbort/g; if ($outFile eq $inFile) { die ("Need an output file, or a .trizbort input file."); } }
    runOneRedact();
  }
}

sub runOneRedact
{
open(A, "$inFile") || die ("No $inFile");
open(B, ">$outFile") || die ("Can't open $outFile");

while ($a = <A>)
{
  if ($a =~ /<room id=/)
  {
    $reg = lc(tag($a, "region"));
	$reg =~ s/ /____/g;
	$id = tag($a, "id");
	print tag($a, "name") . " in " . $reg . "\n";
    if ($redact{$reg})
	{
	  $blockId{$id} = 1;
	  print "Blocking ID $id in " . tag($a, "name") . "\n";
	  if ($a !~ /\/>/)
	  {
	    while (($b = <A>) !~ /<\/room>/)
		{ }
		next;
	  }
	  else
	  {
	    print "Self closing $a";
	    next;
	  }
	}
  }
  elsif ($a =~ /<line id=/)
  {
    $b = <A>;
    $c = <A>;
    $d = <A>;
	if ($blockId{tag($b, "id")} || $blockId{tag($c, "id")})
	{
	  #print "Line $b$c blocked.";
	  next;
	}
	$a = "$a$b$c$d";
	#print "OK: $a";
  }
    print B "$a";
}

close(A);
close(B);

}

sub tag
{
  my $q = $_[0]; chomp($q);
  $q =~ s/.*\b$_[1]=\"//g;
  $q =~ s/\".*//g;
  return lc($q);
}

sub usage
{
print<<EOT;
-p = specify parameter file
-pd = default parameter file c:\\tech\\trizbort\\redact.txt
-c = clear hash
-r = redactable regions
-f = in file
-o = out file
EOT
exit
}