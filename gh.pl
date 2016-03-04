use strict;
use warnings;

use File::Compare;

my $alph = 1;
my $procString="shu,roi,sts";

my $ght = "c:\\writing\\scripts\\gh.txt";
my $ghs = "c:\\writing\\scripts\\gh.pl";

my $defaultString = "as";

preProcessHashes();

#these can't be changed on the command line. I'm too lazy to write in command line parsing right now, so the
my $justPrint = 0;
my $verbose = 0;
my $myBase = "";

my $gh = "c:\\users\\andrew\\Documents\\github";
my $count = 0;
my $a;
my %altHash, my %do, my %poss;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  for ($a)
  {
  /^(-e|e)$/ && do { system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ght"); $count++; exit; };
  /^(-c|c)$/ && do { system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ghs"); $count++; exit; };
  /-j/ && do { $justPrint = 1; $count++; next; };
  /-v/ && do { $justPrint = 1; $count++; next; };
  /^[a-z34]/ && do { if ($altHash{$ARGV[0]}) { print "$ARGV[0] => $altHash{$ARGV[0]}\n"; $procString = $altHash{$ARGV[0]}; } else { $procString = $ARGV[0]; } $count++; next; };
  /^-\?/ && do { usage(); };
  print "$a not recognized.\n";
  usage();
  }
}

if (!$procString) { $procString = $defaultString; print "Default string: $procString\n"; }

findTerms();

my @procAry = split(/,/, $procString);

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
for my $k (sort keys %poss) { if ($k =~ /,/) { print "$k is a valid key and maps to multiple others.\n"; } else { print "$k is a valid key.\n"; } }
}

processTerms();

##########################################
#the main function

sub processTerms
{
  my @d;
  my $copies = 0; my $unchanged = 0; my $wildcards = 0; my $badFileCount = 0; my $didOne = 0;
  my $badFileList = "";
  my $outName;
  my $fileList = "";
  my $dirName = "";
  my $fromBase="", my $toBase="";
  open(A, $ght) || die ("No $ght");
  while ($a = <A>)
  {
    chomp($a);
    my $b = $a;
	 if ($a =~ /FROMBASE=/) { $fromBase = $a; $fromBase =~ s/^FROMBASE=//g; }
	 if ($a =~ /TOBASE=/) { $toBase = $a; $toBase =~ s/^TOBASE=//g; }

    $b =~ s/=.*//g;

    if (hasHash($b))
    {
	  $didOne = 1; my $wc = "";
      my $c = $a; $c =~ s/.*=//g; @d = split(/,/, $c);
	  my $fromFile = $d[0];
	  my $toFile = $d[1];
	  
	  if ($fromFile !~ /:/) { $fromFile = "$fromBase\\$fromFile"; }
	  if ($toBase) { $toFile = "$toBase\\$d[1]"; }
	  

	  if ((! -f $fromFile)  && ($fromFile !~ /\*/)) { print "Oops $fromFile can't be found.\n"; $badFileList .= "$fromFile\n"; $badFileCount++; next; }
	  
	  if ($toFile) { $dirName = $toFile; } elsif (!$dirName) { die("Need dir name to start a block of files to copy."); } else  { print"$fromFile has no associated directory, using $dirName\n"; }

	  if (-d "$gh\\$toFile") { my $short = $fromFile; $short =~ s/.*[\\\/]//g; $outName = "$gh\\$toFile\\$short"; } else { $outName = "$gh\\$toFile"; }
	  if (compare($fromFile, "$outName"))
	  {
	  my $thisWild = 0;
      my $cmd = "copy \"$fromFile\" $gh\\$toFile";
	  if ($fromFile =~ /\*/) { $wildcards++; $thisWild = 1; } else { $copies++; }
	  $fileList .= "$fromFile\n";
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
  else { print "Copied $copies file(s), $wildcards wild cards, $unchanged unchanged, $badFileCount bad files.\n"; if ($fileList) { print "====FILE LIST:\n$fileList"; } if ($badFileCount) { print "====BAD FILES ($badFileCount):\n$badFileList\n"; } }
}

##########################
# finds all valid terms in gh.txt
# not individual files, just pc, sa, etc

sub findTerms
{
open(A, $ght) || die ("Oops, couldn't open $ght.");

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

###############################
# this finds similarities e.g. pc~tpc

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
	  my @b = split(/~/, $a);
	  $altHash{$b[0]} = $b[1];
	  #print "@b[0] -> @b[1]\n";
	}
  }
  close(A);
}

sub hasHash
{
  if ($do{$_[0]}) { return 1; }
  if (($altHash{$_[0]}) && ($do{$altHash{$_[0]}})) { return 1; }
  return 0;
}

sub usage
{
print<<EOT;
========USAGE
-e edits gh.txt
-v = verbose output
-j = just print commands instead of executing
-? = this
EOT
exit;
}