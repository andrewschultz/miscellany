########################################################
#
#zupt.pl
#
#given a manifest of files, this zips the latest version into, uh, a zip file
#

use strict;
use warnings;

use Win32::Clipboard;

use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

################constants first
my $zip = Archive::Zip->new();
my $zupt = __FILE__;
my $zupl = $zupt;
$zupt =~ s/pl$/txt/gi; # zupt = file to read, zupl = perl
my $zupp = $zupt; $zupp =~ s/\.txt$/p\.txt/;

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
my $dropBinOpen = 0;
my $dropLinkClip = 0;
my $noExecute = 0;
my $dropCopy = 0;

##################variables
my $count = 0;
my $temp;
my $dropboxLink = "";
my $needExclam = 0;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  if ($a =~ /\?/) { usage(); }
  if ($a =~ /^-[ol]$/) { $openAfter = 1; $count++; print "Launching the output file after creation.\n"; next; }
  if ($a =~ /^-?x$/) { print "Executing optional commands, if there are any.\n"; $executeBeforeZip = 1; $count++; next; }
  if ($a =~ /^-?a$/) { print "Kitchen sink flags for ZUP.\n"; $executeBeforeZip = $dropCopy = $dropBinOpen = $openAfter = 1; $count++; next; }
  if ($a =~ /^-?nx$/) { print "Executing no commands.\n"; $noExecute = 1; exit; }
  if ($a =~ /^-?p$/) { print "Printing result of executed commands, if there are any.\n"; $printExecute = 1; exit; }
  if ($a =~ /^-?dc$/) { print "Copying to Dropbox afterwards.\n"; $dropCopy = 1; $count++; next; }
  if ($a =~ /^-?db$/) { print "Opening dropbox bin directory afterwards.\n"; $dropBinOpen = 1; $count++; next; }
  if ($a =~ /^-?dl(c)?$/) { print "Dropbox link to clipboard.\n"; $dropLinkClip = 1; $count++; next; }
  if ($a =~ /^-?e$/) { print "Opening commands file $zupt.\n"; `$zupt`; exit; }
  if ($a =~ /^-?v$/) { print "Viewing the output file, if there.\n"; $viewFile = 1; $count++; next; }
  if ($a =~ /^-?(c|ee)$/) { print "Opening script file.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $zupl"); exit; }
  if ($a =~ /^-/) { print "Bad flag $a.\n"; usage(); }
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

readZupFile($zupt);
readZupFile($zupp);

if (!$triedSomething) { print "Didn't find any projects in (@ARGV).\n"; }

if ($dropCopy)
{
  print "Starting Dropbox copy...\n";
  `dropbox.pl -x`;
  print "Dropbox copy done.\n";
}

if ($dropBinOpen)
{
  `start https://www.dropbox.com/home/bins`;
}

#################################
#subroutines
#

sub readZupFile
{

$count = 0;
$zipUp = 0;

open(A, $_[0]) || die ("$_[0] not available, bailing.");

while ($a = <A>)
{
  chomp($a);

  $a =~ s/\%/$version/g;

  #print "$a: ";

  if ($a =~ /^name=/i)
  {
    if ($needExclam) { die ("Need exclamation mark before $a"); }
    $a =~ s/^name=//gi;
    my @b = split(/,/, $a);
	for my $idx(@b)
	{
	  #print "$idx\n";
	  if (defined($here{$idx}) && ($here{$idx}==1))
	  {
	    $needExclam = 1;
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
    $needExclam = 0;
    if ($dropLinkClip)
	{
	  print "There is no dropbox link clip for this project.\n";
	  exit;
	}
	if (!$outFile) { die("OutFile not defined. You need a line with out=X.ZIP in $_[0]."); }
    print "Writing to c:/games/inform/zip/$outFile...\n";
	die 'write error' unless $zip->writeToFileNamed( "c:/games/inform/zip/$outFile" ) == AZ_OK;
	print "Writing successful.\n";
	if ($openAfter) { print "Opening...\n"; `c:\\games\\inform\\zip\\$outFile`; }
	return;
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
  /^>>/ && do { if ($noExecute) { next; } my $cmd = $a; $cmd =~ s/^>>//g; print "Running $cmd\n"; $temp = `$cmd`; if ($printExecute) { print $temp; } next; };
  /^x:i/ && do
  {
    if ($executeBeforeZip && !$noExecute)
	{
	  my $cmd = $a; $cmd =~ s/^x://gi;
	  print "Running $cmd\n"; $temp = `$cmd`;
	  if ($printExecute) { print $temp; }
    }
	next;
  };
  /^dl=/i && do
  {
    $dropboxLink = $a;
	$dropboxLink =~ s/^dl=//i;
	if ($dropLinkClip)
	{
      my $clip = Win32::Clipboard::new();
	  $clip->Set("$dropboxLink");
	  print "$dropboxLink\n";
	  exit();
	}
	next;
  };
  /^D=/i && do
  {
    $b = $a; $b =~ s/^d=//i;
	$b =~ s/\\/\//g;
	$zip->addDirectory("$b");
	next;
  };
  /^F=/i && do
  {
    if ($a =~ /\\/) { warn("WARNING Line $. ($a) has wrong slash direction.\n"); }
    $a =~ s/^F=//gi;
	$a =~ s/\\/\//g;
    #$fileName =~ s/\./_release_$a\./g;
	$b = $a;
	if ($b =~ /\t/)
	{
	  $b =~ s/.*\t//;
	  $a =~ s/\t.*//;
	}
	else
	{
	$b =~ s/.*[\\\/]//g;
	}
	if ((! -f "$a") && (! -d "$a") && ($a !~ /\*/)) { print "No file/directory $a.\n"; }
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

}

sub processCmd
{
  print "$_[0]\n";
  `$_[0]`;
}

sub usage
{
print<<EOT;
USAGE: zupt.pl (project)
-e open commands file zup.txt
-c/ee open script file zup.pl
-db open Dropbox bin after
-dc copies over to Dropbox after
-[ol] open after
-p print command execution results
-v view output zip file if already there
-x execute optional commands
-nx execute nothing (overrides -x)
-dl get dropbox link if available (overrides creating a zip)
-a = -x -db -dc -o
EOT
exit;
}