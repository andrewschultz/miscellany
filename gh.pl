#$procString="shu,roi,sts";

use File::Compare;

$ght = "c:/writing/scripts/gh.txt";

$defaultString = "as";

preProcessHashes();

#these can't be changed on the command line. I'm too lazy to write in command line parsing right now, so the
$justPrint = 0;
$verbose = 0;

$gh = "c:\\users\\andrew\\Documents\\github";

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  for ($a)
  {
  /-j/ && do { $justPrint = 1; $count++; next; };
  /-v/ && do { $justPrint = 1; $count++; next; };
  /^[a-z34]/ && do { if ($altHash{@ARGV[0]}) { print "@ARGV[0] => $altHash{@ARGV[0]}\n"; $procString = $altHash{@ARGV[0]}; } else { $procString = @ARGV[0]; } $count++; next; };
  /^-\?/ && do { usage(); };
  print "$a not recognized.\n";
  usage();
  }
}

if (!$procString) { $procString = $defaultString; print "Default string: $procString\n"; }

findTerms();

@procAry = split(/,/, $procString);

for (@procAry)
{
  if ($_ eq "-a")
  { $alph = 1; next; }
  if ($altHash{$_}) { $do{$altHash{$_}} = 1; print "$_ => $altHash{$_}\n"; }
  else
  {
  $do{$_} = 1;
  }
}

if ($verbose)
{
for $k (sort keys %poss) { if ($k =~ /,/) { print "$k is a valid key and maps to multiple others.\n"; } else { print "$k is a valid key.\n"; } }
}

processTerms();

sub processTerms
{
  $copies = 0; $unchanged = 0; $wildcards = 0; $badFileCount = 0;
  $dirName = "";
  open(A, $ght) || die ("No $ght");
  while ($a = <A>)
  {
    chomp($a);
    $b = $a;
    $b =~ s/=.*//g;
    if ($do{$b})
    {
	  $didOne = 1; $wc;
      $c = $a; $c =~ s/.*=//g; @d = split(/,/, $c);

	  if ((! -f @d[0])  && (@d[0] !~ /\*/)) { print "Oops @d[0] can't be found.\n"; $badFiles .= "@d[0]\n"; $badFileCount++; next; }
	  
	  if (@d[1]) { $dirName = @d[1]; } elsif (!$dirName) { die("Need dir name to start a block of files to copy."); } else  { print"@d[0] has no associated directory, using $dirName\n"; }

	  if (-d "$gh\\@d[1]") { $short = @d[0]; $short =~ s/.*[\\\/]//g; $outName = "$gh\\@d[1]\\$short"; } else { $outName = "$gh\\@d[1]"; }
	  if (compare(@d[0], "$outName"))
	  {
      $cmd = "copy \"@d[0]\" $gh\\@d[1]";
	  if (@d[0] =~ /\*/) { $wildcards++; $thisWild = 1; } else { $copies++; }
	  $fileList .= "@d[0]\n";
	  if ($justPrint) { print "$cmd\n"; } else { $wc = `$cmd`; if ($thisWild) { print "====WILD CARD COPY-OVER OUTPUT\n$wc"; } }
	  }
	  else
	  {
	  $unchanged++;
	  }
#      `$cmd`;
    }
  }
  if (!$didOne) { print "Didn't find anything for $procString."; }
  else { print "Copied $copies file(s), $wildcards wild cards, $unchanged unchanged, $badFileCount bad files.\n"; if ($fileList) { print "====FILE LIST:\n$fileList"; } if ($badFileCount) { print "====BAD FILES ($badFileCount):\n$badFiles\n"; } }
}

##########################
# finds all valid terms

sub findTerms
{
open(A, $ght) || die ("Oops, couldn't open gh.txt.");

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /~/) { next; } #congruency
  if ($a =~ /^d:/) { next; } #default
  if ($a =~ /^;/) { last; }
  if ($a =~ /^#/) { next; }
  if ($a !~ /[a-z]/i) { next; }
  $a =~ s/=.*//g;
  $poss{$a} = 1;
}

close(A);
}

sub preProcessHashes
{
  open(A, "$ght") || die ("Can't open $ght.");
  while ($a = <A>)
  {
    chomp($a);
    if ($a =~ /^d:/)
	{
	  $procString = $a;
	  $procString =~ s/^d://gi;
	}
	if ($a =~ /~/)
	{
	  @b = split(/~/, $a);
	  $altHash{@b[0]} = @b[1];
	  #print "@b[0] -> @b[1]\n";
	}
  }
  close(A);
}

sub usage
{
print<<EOT;
========USAGE
-v = verbose output
-j = just print commands instead of executing
-? = this
EOT
exit;
}