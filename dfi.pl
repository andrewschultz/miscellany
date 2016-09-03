#########################################
#dfi.pl
#sorts out files in the daily directory

use strict;
use warnings;

my %ignore;

my $notallnum = 0;
my $unconv = 0;
my $veryold = 0;
my $misc = 0;
my $zb = 0;

my $daily = "c:/writing/daily";

my @olds = ();
my @odd = ();
my @days = ();
my @notall = ();
my @zerob = ();
my @reserved = ("f.otl", "hthws.txt", "limericks.otl", "undef.txt");

opendir(DIR, $daily);

my @dfi = readdir(DIR);

for (@reserved) { $ignore{$_} = 1; }

for my $x (@dfi)
{
  if (-d "$daily\\$x") { next; }
  if (-s "$daily\\$x" == 0) { $zb++; push(@zerob, $x); next; }
  if ($x =~ /^2016[0-9]{4}\.txt$/i) { $unconv++; push (@days, $x); next; }
  if ($x =~ /^2016/) { $notallnum++; push (@notall, $x); next; }
  if ($x =~ /^200/) { $veryold++; push (@olds, $x); next; }
  if (defined($ignore{$x})) { next; }
  $misc++; push (@odd, $x);
}

print "TEST RESULTS: unconverted,$unconv,3,0,@days\n";
print "TEST RESULTS: notallnum,$notallnum,3,0,@notall\n";
print "TEST RESULTS: misc,$misc,3,0,@odd\n";
print "TEST RESULTS: zero-byte,$zb,3,0,@zerob\n";
