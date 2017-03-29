########################################################
#
#zup.pl
#
#given a manifest of files, this zips the latest version into, uh, a zip file
#

use strict;
use warnings;

use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

################constants first
my $zip = Archive::Zip->new();
my $zup = __FILE__;
my $zupl = $zup; $zupl =~ s/pl$/txt/gi;

##################options
my %here;
my $zipUp = 0;
my $triedSomething = 0;
my $version = 0;
my $openAfter = 0;
my $viewFile = 0;
my $outFile = "";
my $executeBeforeZip = 0;
my $printExecute = 0;

##################variables
my $count = 0;
my $temp;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  if ($a =~ /\?/) { usage(); }
  if ($a =~ /^-[ol]$/) { $openAfter = 1; $count++; next; }
  if ($a =~ /^-?x$/) { print "Executing commands, if there are any.\n"; $executeBeforeZip = 1; exit; }
  if ($a =~ /^-?p$/) { print "Printing result of executed commands, if there are any.\n"; $printExecute = 1; exit; }
  if ($a =~ /^-?e$/) { print "Opening commands file.\n"; `$zup`; exit; }
  if ($a =~ /^-?v$/) { print "Viewing the output file, if there.\n"; $viewFile = 1; $count++; next; }
  if ($a =~ /^-?ee$/) { print "Opening script file.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $zupl"); exit; }
  if ($a =~ /,/)
  {
    my @commas = split(/,/, $count);
	for (@commas) { $here{$_} = 1; }
  }
  else
  {
  $here{$ARGV[$count]} = 1;
  }
  $count++;
}

my $timestamp = "c:\\games\\inform\\zip\\timestamp.txt";

open(A, ">$timestamp");

my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time());
print A sprintf("%d-%02d-%02d %d:%02d:%02d\n", $yearOffset+1900, $month+1, $dayOfMonth, $hour, $minute, $second);
close(A);

$count = 0;

open(A, $zup) || die ("$zup not available, bailing.");

while ($a = <A>)
{
  chomp($a);

  $a =~ s/\%/$version/g;

  #print "$a: ";

  if ($a =~ /^name=/i)
  {
    $a =~ s/^name=//gi;
    my @b = split(/,/, $a);
	for my $idx(@b)
	{
	  #print "$idx\n";
	  if (defined($here{$idx}) && ($here{$idx}==1))
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
  /^v=/i && do { $a =~ s/^v=//gi; $version = $a; next; };
  /^!/ && do
  {
    print "Writing to c:/games/inform/zip/$outFile...\n";
	die 'write error' unless $zip->writeToFileNamed( "c:/games/inform/zip/$outFile" ) == AZ_OK;
	print "Writing successful.\n";
	if ($openAfter) { print "Opening...\n"; `c:\\games\\inform\\zip\\$outFile`; }
	exit;
  };
  /^out=/i && do
  {
    $a =~ s/^out=//gi;
	$outFile = $a;
	if ($viewFile)
	{
	  if (-f "$outFile") { `$outFile`; }
	  else { print "No file $outFile.\n"; }
	  exit();
    }
	$zip = Archive::Zip->new();
	next;
  };
  /^tree:/i && do { $a =~ s/^tree://gi; my @b = split(/,/, $a); $zip->addTree("$b[0]", "$b[1]" ); #print "Added tree: $b[0] to $b[1].\n";
  next; };
  /^>>/ && do { my $cmd = $a; $cmd =~ s/^>>//g; print "Running $cmd\n"; $temp = `$cmd`; if ($printExecute) { print $temp; } next; };
  /^x:i/ && do { if ($executeBeforeZip) { my $cmd = $a; $cmd =~ s/^x://gi; print "Running $cmd\n"; $temp = `$cmd`; if ($printExecute) { print $temp; } } next; };
  /^F=/i && do
  {
    $a =~ s/^F=//gi;
    #$fileName =~ s/\./_release_$a\./g;
	if ((! -f "$a") && (! -d "$a") && ($a !~ /\*/)) { print "No file/directory $a.\n"; }
	$b = $a; $b =~ s/.*[\\\/]//g;
    $zip->addFile("$a", "$b");
	#print "Writing $a to $b.\n";
    next;
  };
  /^c:/i && do
  {
    my $cmd .= " \"$a\"";
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
-[ol] open after
-e open commands file zup.txt
-ee open script file zup.pl
-v view output zip file if already there
-x execute optional commands
-p print command execution results
EOT
exit;
}