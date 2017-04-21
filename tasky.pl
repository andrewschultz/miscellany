################################
#
# tasky.pl
#
# tracks the tasks I want and need to do
#

use strict;
use warnings;

my %short;
my %halfhr;
my %reremind;
my %lastdone;
my %lastwarn;

my $parseAll = 0;
my $modifyTimesFile = 0; # most of the time we will want to modifyTimesFile the data in tasky.txt, but if we are testing, we want to set this to zero. (ACTIVE)
my $launchAfter = 0; # most of the time we will want to modifyTimesFile the data in tasky.txt, but if we are testing, we want to set this to zero. (LAUNCH)

my $key;

my $taskFile = __FILE__;
my $taskText = __FILE__;
$taskText =~ s/pl$/txt/i;
my $taskTest = $taskText;
$taskTest =~ s/\.txt/-test.txt/i;
my $taskHtm = __FILE__;
$taskHtm =~ s/pl$/htm/i;

open(A, $taskText);
while ($a = <A>)
{
  if ($a =~ /^#/) { next; }
  if ($a =~ /^;/) { next; }
  chomp($a);
  my @l = split(/\t/, $a);
  if ($l[0] eq "ACTIVE") { $modifyTimesFile = $l[1]; next; }
  if ($l[0] eq "LAUNCH") { $launchAfter = $l[1]; next; }
  $short{$l[0]} = $l[1];
  $halfhr{$l[0]} = $l[2];
  $reremind{$l[0]} = $l[3];
  $lastdone{$l[0]} = $l[4];
  $lastwarn{$l[0]} = $l[5];
}

close(A);

if ($ARGV[0])
{
  my $arg = lc($ARGV[0]);
  for ($arg)
  {
  /^t$/i && do { my $time = time(); if (defined($ARGV[1])) { $time -= $ARGV[1]; } print "Time: $time\n"; exit(); };
  /^-?test$/ && do { $modifyTimesFile = 0; };
  /^-?real$/ && do { $modifyTimesFile = 1; };
  /^-?c$/ && do { `start "" notepad++ __FILE__`; exit(); };
  /^-?e$/ && do { `start "" notepad++ $taskText`; exit(); };
  /^-\?$/ && do { listArgs(); print "-? shows these all\n-test in test mode (tasky.txt not updated)\n-c open the source\n-e open tasky.txt\n-ee open tasky-test.txt\n-real in real mode (tasky.txt updated)\n"; exit(); };
  }
  if ($short{$arg})
  {
    $lastdone{$arg} = time();
    reprintTaskFile();
  }
  else
  {
    print "No task $arg-- -? gives full options.\n";
	listArgs();
  }
  exit();
}

my $time = time();
my $timeTo = "";

for $key (sort keys %short)
{
  if ($lastdone{$key} + 1790 * $halfhr{$key} >= $time) # ok, if we have done the task recently, skip it
  {
    next;
  }
  if ($lastwarn{$key} <= $lastdone{$key}) # if we haven't given an initial warning yet...
  {
    $timeTo .= "<font size=+5><center>FIRST REMINDER: $short{$key}</center></font>\n";
    $lastwarn{$key} = $time;
	next;
  }
  #print ($lastdone{$key} + 3580 * $halfhr{$key} - $time);
  #printf("$key: %d to %d, but it's $time now.\n", $lastdone{$key} + 1790 * $halfhr{$key}, $lastdone{$key} + 3580 * $halfhr{$key});
  if (($lastdone{$key} + 3580 * $halfhr{$key} < $time) && (!$parseAll))
  {
    printf("$key\'s warning time ranges from %d to %d, but it's $time now.\n", $lastdone{$key} + 1790 * $halfhr{$key}, $lastdone{$key} + 3580 * $halfhr{$key});
    next;
  }
  $lastwarn{$key} = $time;
  $timeTo .= "<font size=+5><center>RE-REMINDER: $short{$key}</center></font>\n";
}

if ($timeTo)
{
  my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time());
  my $timeStr = sprintf("%02d-%02d-%02d %02d:%02d:%02d", $yearOffset+1900, $month, $dayOfMonth, $hour, $minute, $second);
  open(A, ">$taskHtm");
  print A "<html><title>Tasks to do</title><body bgcolor=red><center><img src=siren.gif><img src=siren.gif><img src=siren.gif><img src=siren.gif><img src=siren.gif></center><font size=+5><center>$timeStr to-do</center></font><br />$timeTo<center><img src=siren.gif><img src=siren.gif><img src=siren.gif><img src=siren.gif><img src=siren.gif></center></body></html>";
  close(A);
  `$taskHtm`;
}

if ($timeTo)
{
reprintTaskFile();
}

###############################################

sub reprintTaskFile
{
  my $outString;
  my @r;
  open(A, "$taskText");
  while ($a = <A>)
  {
    @r = split(/\t/, $a);
	if ($r[0] eq "ACTIVE") { $outString .= "ACTIVE\t$modifyTimesFile\n"; next; }
	if ($short{$r[0]})
	{
	  $outString .= "$r[0]\t$short{$r[0]}\t$halfhr{$r[0]}\t$reremind{$r[0]}\t$lastdone{$r[0]}\t$lastwarn{$r[0]}\n";
	}
	else { $outString .= $a; }
  }
  close(A);
  my $theFile = $taskTest;
  if ($modifyTimesFile)
  {
    $theFile = "$taskText";
  }
  open(A, ">$theFile");

  print A $outString;
  close(A);
}

sub listArgs
{
  for my $k (sort keys %short)
  {
    print "$k: $short{$k}\n";
  }
}