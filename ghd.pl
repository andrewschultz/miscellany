#######################################
#ghd.pl: github documenter
#
#did I do something today?
#no arguments. Set to run at 11:30 PM.
#
#requires ghd.txt to see where to sort which projects
#
#BASE=c:\users\me\documents\github
#github=threediopolis
#bitbucket=fourdiopolis

use POSIX qw(strftime getcwd);
use Win32;

use strict;
use warnings;

########################hashes
my %repo;
my %repoSum;
my %count;
my %siteArray;

################options
my $debug     = 0;
my $popup     = 0;
my $unchAfter = 0;

#######################variables
my $count  = 0;
my $ghBase = "";
my $popupText;
my $overallSum;
my $sum;
my $daysAgo = 0;

chdir("c:\\writing\\scripts");
my $siteFile = __FILE__;
$siteFile =~ s/pl$/txt/i;

while ( $count <= $#ARGV ) {
  my $arg = $ARGV[$count];
  for ($arg) {
    /^-?c$/ && do {
      `start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"`;
      exit();
    };
    /^-?d$/ && do { $debug     = 1; $count++; next; };
    /^-?p$/ && do { $popup     = 1; $count++; next; };
    /^-?u$/ && do { $unchAfter = 1; $count++; next; };
    /^-?[es]$/ && do { `$siteFile`; exit(); };
    /^-?\d+$/ && do {
      $daysAgo = $ARGV[0];
      $daysAgo = abs($daysAgo);
      print "$daysAgo day(s) ago.\n";
      $count++;
      next;
    };
    /^-?\?/ && do { usage(); };
    print "Unknown cmd line parameter $arg\n";
    usage();
  }
}

$popupText = strftime "Results for %m/%d/%Y\n", localtime( time() - 86400 );

open( A, "$siteFile" ) || die("Could not find $siteFile, bailing.");
while ( $a = <A> ) {
  chomp($a);
  if ( $a =~ /^base=/i ) { $a =~ s/^base=//i; $ghBase = $a; next; }
  my @b = split( /:/, $a );
  my @c = split( /,/, $b[1] );
  $siteArray{ $b[0] } = \@c;
  print "Defining siteArray $b[0] = $b[1]\n" if $debug;
  for (@c) { $repo{$_} = $b[0]; }
}

close(A);

unless ($ghBase) { die("Need BASE= in $siteFile."); }
unless ( -d "$ghBase" ) {
  die("$ghBase in $siteFile is not a valid directory.");
}

my @repos = ();
for ( sort keys %siteArray ) {
  @repos = ( @repos, @{ $siteArray{$_} } );
}

my $r;
my $thisLog = "";
my $cmd =
  $daysAgo
  ? sprintf( "git log --since=\"%d days ago\" --until=\"%d days ago\"",
  $daysAgo, $daysAgo - 1 )
  : "git log --since=\"12 am\""
  ;    #yes, git log accepts "1 days ago" which is nice

print "Running on all dirs: $cmd\n";

for $r (@repos) {
  chdir("$ghBase\\$r") or do { warn "fail $ghBase\\$r"; next; };
  print "$ghBase\\$r : $cmd\n" if $debug;
  $thisLog = `$cmd`;
  print getcwd() . ": $cmd\n" . cutDown($thisLog) if $debug;
  $count{$r} = () = $thisLog =~ /([\n]|^)commit/gi;
  $repoSum{ $repo{$r} } += $count{$r};
}

for my $k ( sort { $repo{$a} cmp $repo{$b} || $a cmp $b } keys %count ) {
  if ( $count{$k} ) { $popupText .= "====$k($repo{$k}): $count{$k}\n"; }
}
$popupText .= "Repos above, sites below\n";
for my $k ( sort keys %repoSum ) {
  $popupText .= "====$k: $repoSum{$k}\n";
  if ( ( !$repoSum{$k} ) && ( !$daysAgo ) ) {
    if ($popup) {
      `c:\\nightly\\see-$k.htm`;
    }
    else {
      print "\n*************************SEE $k today ("
        . ( join( ", ", @{ $siteArray{"newproj"} } ) ) . ")\n\n";
    }
  }
  $overallSum += $repoSum{$k} ? $repoSum{$k} - 1 : 0;
}

if ($overallSum) {
  $popupText .=
"====$overallSum total extra changes\nRun UNCH.PL to see if there are any more to commit/push.\nRun gh.pl alb/all (all but/all, 2nd includes private repos) to copy over straggler files.";
}

if ($popup) {
  Win32::MsgBox( "$popupText", 0, "GHD.PL" );
}
else {
  print "$popupText";
}

if ($unchAfter) {
  `unch.pl -h`;
}

#######################################
#subroutines

sub cutDown {
  my @x      = split( /\n/, $_[0] );
  my $count  = 0;
  my $c      = 0;
  my $retVal = "";
  while ( $#x > $c * 6 ) {
    $x[ 2 + $c * 6 ] =~ s/^Date/'Date ' . ($c+1)/e;
    $retVal .= "$x[2+$c*6]\nChange " . ( $c + 1 ) . ":$x[4+$c*6]\n";
    $c++;
  }

  return $retVal;
}

sub usage {
  print <<EOT;
==========basic usage==========
-c open this source
-d debug (or detail, to see log details)
-p pop up results
-[es] open site file
-u run unch.pl afterwards
-v verbose (shows commands etc.)
-(#) how many days back (default = 0, today)
EOT
  exit();
}
