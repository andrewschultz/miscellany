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
my @voldies = ();
my @reserved = ("f.otl", "hthws.txt", "limericks.otl", "undef.txt");

opendir(DIR, $daily);

my @dfi = readdir(DIR);

for (@reserved) { $ignore{$_} = 1; }

for my $x (@dfi)
{
  if (! -f "$daily\\$x") { next; }
  if (-d "$daily\\$x") { next; }
  if (-s "$daily\\$x" == 0) { print "0: $daily\\$x\n"; $zb++; push(@zerob, $x); next; }
  if ($x =~ /^2016[0-9]{4}\.txt$/i) { $unconv++; push (@days, $x); next; }
  if ($x =~ /^2016/) { $notallnum++; push (@notall, $x); next; }
  if ($x =~ /^200/) { $veryold++; push (@voldies, $x); next; }
  if (defined($ignore{$x})) { next; }
  $misc++; push (@odd, $x);
}

print "TEST RESULTS: unconverted <b>DFI.PL</b>,3,$unconv,0,@days\n";
print "TEST RESULTS: notallnum <b>DFI.PL</b>,3,$notallnum,0,@notall\n";
print "TEST RESULTS: very old <b>DFI.PL/COV.PL</b>,3,$veryold,0,@voldies\n";
print "TEST RESULTS: misc <b>DFI.PL</b>,3,$misc,0,@odd\n";
print "TEST RESULTS: zero-byte <b>DFI.PL</b>,3,$zb,0,@zerob\n";
