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
my $overwriteData = 0; # most of the time we will want to overwrite the data in tasky.txt, but if we are testing, we want to set this to zero.

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
  /^-?c$/ && do { `start "" notepad++ __FILE__`; exit(); };
  /^-?e$/ && do { `start "" notepad++ $taskText`; exit(); };
  /^-\?$/ && do { listArgs(); exit(); };
  }
  if ($short{$arg})
  {
    $lastdone{$arg} = time();
    reprintTaskFile();
  }
  else
  {
    print "No task $arg.\n";
	listArgs();
  }
  exit();
}

my $time = time();
my $timeTo = "";

for $key (sort keys %short)
{
  if ($lastdone{$key} + 1790 * $halfhr{$key} < $time) # 1790 is a fudge factor that accounts for timing not being perfect, instead of 1800
  {
    if (($lastdone{$key} + 3600 * $halfhr{$key} > $time) && (!$parseAll))
	{
	  next;
	}
    if ($lastwarn{$key} >= $lastdone{$key})
	{
	  if ($lastwarn{$key} + $reremind{$key} * 1790 < $time)
	  {
	    $lastwarn{$key} = $time;
	    $timeTo .= "<font size=+5><center>RE-REMINDER: $short{$key}</center></font>\n";
		next;
	  }
	}
    $lastwarn{$key} = time();
    $timeTo .= "<font size=+5><center>FIRST REMINDER: $short{$key}</center></font>\n";
    $lastwarn{$key} = $time;
  }
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

reprintTaskFile();

###############################################

sub reprintTaskFile
{
  my $outString;
  my @r;
  open(A, "$taskText");
  while ($a = <A>)
  {
    @r = split(/\t/, $a);
	if ($short{$r[0]})
	{
	  $outString .= "$r[0]\t$short{$r[0]}\t$halfhr{$r[0]}\t$reremind{$r[0]}\t$lastdone{$r[0]}\t$lastwarn{$r[0]}\n";
	}
	else { $outString .= $a; }
  }
  close(A);
  my $theFile = $taskTest;
  if ($overwriteData)
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