use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

my $zip = Archive::Zip->new();

$zup = "c:/writing/scripts/zup.txt";
$zupl = "c:/writing/scripts/zup.pl";
open(A, $zup) || die ("$zup not available, bailing.");

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  if ($a =~ /\?/) { usage(); }
  if ($a =~ /^-o$/) { $openAfter = 1; $count++; next; }
  if ($a =~ /^e$/) { print "Opening commands file.\n"; `$zup`; exit; }
  if ($a =~ /^ee$/) { print "Opening script file.\n"; `$zupl`; exit; }
  if ($a =~ /,/)
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
  
  $a =~ s/\%/$version/g;

  #print "$a: ";

  if ($a =~ /^name=/i)
  {
    $a =~ s/^name=//gi;
    @b = split(/,/, $a);
	for $idx(@b)
	{
	  #print "$idx\n";
	  if ($here{$idx}==1)
	  {
	    $triedSomething = 1;
	    $zipUp = 1;
	  }
	}
  }
  if ($a =~ /^;/) { last; }
  if (!$zipUp) { next; }

  for ($a)
  {
  /^v=/ && do { $a =~ s/^v=//g; $version = $a; next; };
  /^!/ && do
  {
    print "Writing to c:/games/inform/zip/$outFile...\n";
	die 'write error' unless $zip->writeToFileNamed( "c:/games/inform/zip/$outFile" ) == AZ_OK;
	print "Writing successful.\n";
	if ($openAfter) { print "Opening...\n"; `c:\\games\\inform\\zip\\$outFile`; }
	exit;
  };
  /^out=/ && do { $a =~ s/^out=//g; $outFile = $a; $zip = Archive::Zip->new(); next; };
  /^tree:/ && do { $a =~ s/^tree://g; @b = split(/,/, $a); $zip->addTree("@b[0]", "@b[1]" ); #print "Added tree: @b[0] to @b[1].\n";
  next; };
  /^>>/ && do { $cmd = $a; $cmd =~ s/^>>//g; `$cmd`; print "Running $cmd\n"; next; };
  /^F=/i && do
  {
    $a =~ s/^F=//gi;
    #$fileName =~ s/\./_release_$a\./g;
    $needFile = 0;
	if ((! -f "$a") && (! -d "$a") && ($a !~ /\*/)) { print "No file/directory $a.\n"; }
	$b = $a; $b =~ s/.*[\\\/]//g;
    $zip->addFile("$a", "$b");
	#print "Writing $a to $b.\n";
    next;
  };
  /^c:/ && do
  {
    $cmd .= " \"$a\"";
    if ((! -f "$a") && (! -d "$a")) { print "WARNING: $a doesn't exist.\n"; }
    $zip->addFile("$a");
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

sub usage
{
print<<EOT;
USAGE: zup.pl (project)
EOT
exit;
}