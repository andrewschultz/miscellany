############################################
#hrcheck.pl (formerly sov.pl for stack overflow stuff)
#
#scheduling stuff, and stuff
#hrcheck.txt edited for what, when
#
#example of one line:
#
#11|FFX "http://www.thefreedictionary.com"
#
#Weekly thing
#5|8|FFX "http://btpowerhouse.com"
#
#tphb = quarter hours
#:(0-5) = 0 past, 10 past, etc.

use strict;
use warnings;
use POSIX;

my $check = "c:\\writing\\scripts\\hrcheck.txt";
my $check2 = "c:\\writing\\scripts\\hrcheckp.txt";
my $code = "c:\\writing\\scripts\\hrcheck.pl";

my $adjust = 0;
my $cmdCount = 0;

my @times;

my %browsMap;

$browsMap{"FFX"} = "\"C:\\Program Files (x86)\\Mozilla Firefox\\firefox\"";
$browsMap{"OPE"} = "\"C:\\Program Files (x86)\\Opera\\launcher.exe\"";
$browsMap{"CHR"} = "\"C:\\Users\\Andrew\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe\"";

my $min;

my @quarters  = ("t", "p", "h", "b");
my @tens = (0, 0, 0, 0, 0, 0);

if (defined($ARGV[0]))
{
if ($ARGV[0] =~ /^(-|\+)?[0-9]+$/) { $adjust += $ARGV[0]; }
elsif ($ARGV[0] eq "e" || $ARGV[0] eq "-e")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check";
  `$cmd`;
  exit;
}
elsif ($ARGV[0] eq "p" || $ARGV[0] eq "-p")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check2";
  `$cmd`;
  exit;
}
elsif ($ARGV[0] eq "c" || $ARGV[0] eq "-c")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $code";
  `$cmd`;
  exit;
}
else
{
usage();
}
}

my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time + $adjust * 60);

my $defaultBrowser = "";

hrcheck($check);
hrcheck($check2);

sub hrcheck
{
open(A, "$_[0]") || die ("No $_[0]");

my $line;

my @qhr = (0, 0, 0, 0);

my $ignore = 0;

my @b;

while ($line = <A>)
{
  if ($line =~ /^ABORT/i) { die ("Abort found in $_[0], line $.."); }
  if ($line =~ /^--/) { $ignore = 1; next; }
  if ($line =~ /^\+\+/) { $ignore = 0; next; }
  if ($line =~ /^#/) { next; }
  if ($line =~ /^;/) { last; }
  if ($ignore) { next; }
  chomp($line);
  @qhr = (1, 0, 0, 0);
  $modNum = 0;
  if ($line =~ /^DEF=/)
  {
    $defaultBrowser = $line;
	$defaultBrowser =~ s/^DEF=//;
	next;
  }
  $cmdCount = 0;
  my $min = 0;
  @b = split(/\|/, $line);
  if ($#b == 2)
  {
    my @q = split(/,/, $b[0]);
	my $gotOne = 0;
	for (@q)
	{
	  if ($dayOfWeek == $_)
	  {
	    #print "$line: today\n";
		$gotOne = 1;
      }
    }
	if (!$gotOne) { next; }
    $cmdCount++;
  }
  @times = split(/,/, $b[$cmdCount]);

  if ($times[$#times] =~ /[m]$/) { $mod = $times[$#times]; $mod =~ s/.*m//g; }
  
  ######################quarter hours
  if ($times[$#times] =~ /[tphb]$/) { @qhr[0] = 0;
  while ($times[$#times] =~ /[tphb]$/)
  {
    for (0..3)
	{
	  if ($times[$#times] =~ /$quarters[$_]$/)
	  {
	    $qhr[$_] = 1;
		$times[$#times] =~ s/.$//;
      }
    }
  }
  }
  #this needs to be outside the loop so it registers
  $min = floor($minute/15);
 
  if ($times[$#times] =~ /:/)
  {
    @tens = (0, 0, 0, 0, 0, 0);
	my @totens = split(/:/, $times[$#times]);
	$times[$#times] =~ s/:.*//;
	for (1..$#totens) { $tens[$totens[$_]] = 1; }
	$min = floor($minute/10);
  }
  $cmdCount++;

  #print "$b[1]\n"; exit;
  if ($defaultBrowser)
  {
  $b[$cmdCount] =~ s/^DEF/$defaultBrowser/;
  }
  for my $q (keys %browsMap)
  {
  my $name_idx = index $b[$cmdCount], $q;
  if ($name_idx >= 0)
  {
  substr ($b[$cmdCount],
  $name_idx,
  length($q),
  $browsMap{$q} );
  }
  }
  if (validHour())
  {
    if ($qhr[$min] || $tens[$min])
	{
      if (-f "$b[$cmdCount]" && ($b[$cmdCount] =~ /(txt|otl)$/i)) # skip over empty text file
      {
        if (-s "$b[$cmdCount]" == 0) { print "Skipping empty file $b[$cmdCount].\n"; next; }
      }
	  print "Running $b[$cmdCount]\n";
	  print `$b[$cmdCount]`;
	}
  }
}

close(A);
}

sub validHour
{
  my $t = $times[$#times];
  if ($t == $hour) { return 1; }
  if ($t < 0)
  {
    my $mult = - $t;
	if ($hour * 2 % $mult == 0) { return 1; }
  }
  return 0;
}

sub usage
{
print<<EOT;
e = check stuff to check
c = check code
p = check private file
? (or anything else) = usage
EOT
exit;
}