##################################################
#
#redact.pl
#
#redacts rooms with certain regions in Trizbort
#

use warnings;
use strict;
my $debug = 0, my $inFile, my $outFile;
my $keep = 0;
my $allDone = 0;
my @redact;
my %redact;
my %blockId;
my $anythingRead = 0;
my $redactText = 0;

my $count = 0;

if ($#ARGV == -1) { usage(); }

OUTER:
while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  if ($count < $#ARGV) { $b = $ARGV[$count+1]; } else { $b = ""; }
  for ($a)
  {
  /^-d$/ && do { $debug = 1; $count++; next; };
  /^-p$/ && do  { readFile($b); $count+= 2; next; };
  /^-pd$/ && do { readFile("c:\\tech\\trizbort\\redact.txt"); $count++; next; };
  readArray($ARGV + $count);
  last OUTER;
  }
}

if (!$anythingRead) { print "Though the command line had arguments, nothing was processed.\n"; usage(); }

sub readFile
{
  print "Trying file $_[0]\n";
  open(CMD, "$_[0]") || die ("Can't open $_[0]");
  my $a = "";

  while (defined($a = <CMD>) && !$allDone)
  {
  chomp($a);
  readLine($a);
  }
  close(CMD);
}

sub readLine
{
  if ($_[0] =~ /^;/) { $allDone = 1; exit; }
  if ($_[0] =~ /^#/) { return; }
  my @array = ($_[0] =~ /(".*?"|\S+)/g);
  print "Trying line $_[0].\n";
  readArray(@array);
}

sub readArray
{
  my $count = 0;
  my $runThis = 0;
  if (!$keep) { undef(%redact); } else { $keep = 0; }
  
  while ($count <= $#_)
  {
    my $a = $_[$count];
	my $b = $_[$count+1]; if ($b =~ /^\"/) { $b =~ s/\"//g; }
    for ($a)
	{
	/^-k$/ && do { $keep = 1; $count++; next; };
	/^-t$/ && do { $redactText = 1; $count++; next; };
	/^-st$/ && do { $redactText = 0; $count++; next; };
	/^-r$/ && do { @redact = split(/,/, $b); for (@redact) { $redact{"$_"} = 1; } $count += 2; next; };
	/^-f$/ && do { $inFile = $b; $count += 2; $runThis = 1; next; };
	/^-o$/ && do { $outFile = $b; $count += 2; next; };
	/^-d$/ && do { $debug = 1; $count++; next; };
	/^-nd$/ && do { $debug = 0; $count++; next; };
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
my $regions = 0;

while ($a = <A>)
{
  if ($a =~ /<regions>/) { $regions = 1; print B $a; next; }
  if ($a =~ /<\/regions>/) { $regions = 0; print B $a; next; }
  if ($regions) { if ($redact{tag($a, "Name")}) { chomp($a); $a =~ s/^[ \t]+//g; printDebug("Ignoring $a region tag.\n"); next; } }
  if ($a =~ /<room id=/)
  {
    my $reg = lc(tag($a, "region"));
	my $id = tag($a, "id");
	#printDebug(tag($a, "name") . " in " . $reg . "\n");
    if ($redact{$reg})
	{
	  $blockId{$id} = 1;
	  printDebug("Blocking ID $id in " . tag($a, "name") . "\n");
	  if ($a !~ /\/>/)
	  {
	    while ((my $junk = <A>) !~ /<\/room>/)
		{ }
		next;
	  }
	  else
	  {
	    #print "Self closing $a";
	    next;
	  }
	}
  }
  elsif ($a =~ /<line id=/)
  {
    my $b = <A>;
    my $c = <A>;
    my $d = <A>;
	if ($blockId{tag($b, "id")} || $blockId{tag($c, "id")})
	{
	  #print "Line $b$c blocked.";
	  next;
	}
	$a = "$a$b$c$d";
	#print "OK: $a";
  }
    if ($redactText)
	{
	  if ($a =~ /<(room|objects)/)
	  {
	  $a =~ s/(description=|name=)(\"[^\"]*\")/$1 . redactRoomName($2)/eg;
	  $a =~ s/(>[^<]+<)/redactRoomDetails($1)/eg;
	  }
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

sub redactRoomName
{
  my $x = $_[0]; $x =~ s/[^ \"\n]/./g;
  return $x;
}

sub redactRoomDetails
{
  my $x = $_[0]; $x =~ s/[^<> \r\n\|]/./g;
  return $x;
}

sub printDebug
{
  if ($debug == 1) { print "$_[0]"; }
}

sub usage
{
print<<EOT;
========USAGE========
-p = specify parameter file
-pd = default parameter file c:\\tech\\trizbort\\redact.txt
-d = debug on
-nd = debug off
-c = clear hash
-r = redactable regions
-f = in file
-o = out file
EOT
exit
}