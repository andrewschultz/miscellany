##################################################
#
#redact.pl
#
#redacts rooms with certain regions in Trizbort
#

my $defRead = "c:\\tech\\trizbort\\redact.txt";
use warnings;
use strict;
my $debug = 0, my $inFile, my $outFile;
my $keep = 0;
my $allDone = 0;
my $runC = 0;
my @regionRedact;
my %redact;
my %blockId;
my $anythingRead = 0;
my $redactText = 0;
my %runThisGroup;
my @temp;
my $myReadFile = "";

my $count = 0;

if ($#ARGV == -1) { usage(); }

OUTER:
while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  if ($count < $#ARGV) { $b = $ARGV[$count+1]; } else { $b = ""; }
  for ($a)
  {
  $anythingRead = 1;
  /^-?g$/ && do { @temp = split(/,/, $b); for (@temp) { $runThisGroup{$_} = 1; } $count += 2; next; };
  /^-?d$/ && do { $debug = 1; $count++; next; };
  /^-?c$/ && do { $runC = 1; $count++; next; };
  /^-?p$/ && do { $myReadFile = $b; $count+= 2; next; };
  /^-?q$/ && do { $myReadFile = $defRead; $runC = 1; @temp = split(/,/, $b); for (@temp) { $runThisGroup{$_} = 1; } $count += 2; next; };
  /^-?pd$/ && do { $myReadFile = $defRead; $count++; next; };
  /^-?fs$/ && do { showParameterFileSyntax(); };
  /^-?\?$/ && do { usage(); };
  if ($count < $#ARGV)
  {
  readArray(@ARGV[$count..$#ARGV]);
  }
  last OUTER;
  }
}

if ($myReadFile) { readFile($myReadFile); }

if (!$anythingRead) { print "Though the command line had arguments, nothing was processed.\n"; usage(); }

sub readFile
{
  if ($debug) { print "Trying file $_[0]\n"; }
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
  if ($_[0] =~ /^-cf/) { my $temp = $_[0]; $temp =~ s/^-cf +//g; `$temp`; return; } # force no matter what
  my @array = ($_[0] =~ /(".*?"|\S+)/g);
  if ($debug) { print "Trying line $_[0].\n"; }
  readArray(@array);
}

sub readArray
{
  my $count = 0;
  my $runThis = 0;
  if (!$keep) { undef(%redact); } else { $keep = 0; }
  $redactText = 0;
  my @lineGroupList = ();
  my $skipThis = 0;
  my $commandToRun = "";
  my $commandSearch = 0;
  
  MYWHILE:
  while ($count <= $#_)
  {
    my $a = $_[$count];
	my $b = "";
	if (defined $_[$count+1]) { $b = $_[$count+1]; if ($b =~ /^\"/) { $b =~ s/\"//g; } }
	MYFOR:
    for ($a)
	{
	if (($commandSearch) && ($a !~ /^-/)) { last MYWHILE; }
	/^-k$/ && do { $keep = 1; $count++; next; };
	/^-c$/ && do { $commandToRun = join(" ", @_[$count+1..$#_]); last MYWHILE; };
	/^-t$/ && do { $redactText = 1; $count++; next; };
	/^-st$/ && do { $redactText = 0; $count++; next; };
	/^-r$/ && do { @regionRedact = split(/,/, $b); for (@regionRedact) { $redact{"$_"} = 1; } $count += 2; next; };
	/-g$/ && do { $skipThis = 1; @lineGroupList = split(/,/, $b); for (@lineGroupList) { if ($runThisGroup{$_}) { $skipThis = 0; } } $count += 2; next; };
	/-gn$/ && do { $skipThis = 0; @lineGroupList = split(/,/, $b); for (@lineGroupList) { if ($runThisGroup{$_}) { $skipThis = 1; } } $count += 2; next; };
	/^-f$/ && do { $inFile = $b; $count += 2; $runThis = 1; next; };
	/^-o$/ && do { $outFile = $b; $count += 2; next; };
	/^-d$/ && do { $debug = 1; $count++; next; };
	/^-nd$/ && do { $debug = 0; $count++; next; };
	print "Argument $count ($a) unknown.\n";
	usage();
	}
  }
  if ($skipThis) { return; }
  if ($commandToRun) { if ($runC) { print "Running $commandToRun.\n"; `$commandToRun`; } else { print "Use -c to run $commandToRun.\n"; return; } }
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
print "$inFile to $outFile.\n";
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

sub showParameterFileSyntax
{
print<<EOT;
===========redaction file syntax===========
# for comments
; to end the test
-g says which group of files should run something, e.g. -g b,c will run only if the command line has -g b or -g c
-gn is the opposite. If -g or -gn is not specified, the line is run
-d/-nd toggles debug on/off
-t/-rt redacts text, -st shows it
-r region redact
-f to establish in file
-o to establish out file
-c says to run the remaining line text as a command. BE SURE ANY FLAGS ARE SET BEFORE RUNNING -c.
-k keeps what to redact for the next line
EOT
exit
}

sub usage
{
print<<EOT;
========USAGE========
-p = specify parameter file
-pd = default parameter file c:\\tech\\trizbort\\redact.txt
-d = debug on
-nd = debug off
-c = command to run e.g. trizbort -qs (file) for quick-save
-cf = force to run no matter what
-r = redactable regions
-f = in file
-o = out file
-t = redact text
-g = group of commands to run (eg if the file has -g pc, -g pc or -g pc,sc for -g pc and -g sc)
-fs = show parameter file syntax
-q = quickly run everything on a project e.g. -q pc
EOT
exit
}