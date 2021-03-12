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
my %doubleCheck;
my %hasBranch;

################options
my $today_yday = 0;
my $debug     = 0;
my $showLog   = 1;
my $popup     = 0;
my $unchAfter = 0;
my $hours_before     = 0;
my $hours_after     = 0;

#######################variables
my $show_master_main = 0;
my $count  = 0;
my $ghBase = "";
my $popupText;
my $overallSum;
my $sum;
my $daysAgo             = 0;
my $allBranches         = 0;
my $mainBranchWarning = 0;

chdir("c:\\writing\\scripts");
my $siteFile = "c:\\writing\\scripts\\ghd.txt";

while ( $count <= $#ARGV ) {
  my $arg = $ARGV[$count];
  for ($arg) {
    /^-?ab$/ && do { $allBranches = 1; $count++; next; };
    /^-?c$/ && do {
      `start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"`;
      exit();
    };
    /^-?d$/ && do { $debug = 1; $count++; next; };
    /^-?h(-)?[0-9]+$/ && do {
( $hours_before = $arg ) =~ s/^-?h//;
$hours_before = hr_norm($hours_before);
$hours_after = $hours_before;
$count++;
next;
};
    /^-?ha(-)?[0-9]+$/ && do {
( $hours_after = $arg ) =~ s/^-?h//;
$hours_after = hr_norm($hours_before);
$count++;
next;
};
    /^-?hb(-)?[0-9]+$/ && do {
( $hours_before = $arg ) =~ s/^-?h//;
$hours_before = hr_norm($hours_before);
$count++;
next;
};
    /^-?sl$/   && do { $showLog             = 1; $count++; next; };
    /^-?nsl?$/ && do { $showLog             = 0; $count++; next; };
    /^-nmw$/   && do { $mainBranchWarning = 0; $count++; next; };
    /^-mw$/    && do { $mainBranchWarning = 1; $count++; next; };
    /^-?p$/    && do { $popup               = 1; $count++; next; };
    /^-?ty$/    && do { $today_yday           = 1; $count++; next; };
    /^-?u$/    && do { $unchAfter           = 1; $count++; next; };
    /^-?(m|mm)$/    && do { show_shift_branch_name('<your project>'); exit(); };
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

open( A, "$siteFile" ) || die("Could not find $siteFile, bailing.");
while ( $a = <A> ) {
  chomp($a);
  if ( $a =~ /^base=/i ) { $a =~ s/^base=//i; $ghBase = $a; next; }
  my @b = split( /:/, $a );
  my @c = split( /,/, $b[1] );
  for (@c) {
    if ( $_ =~ /\// ) {
      my $temp = $_;
      $temp =~ s/\/.*//;
      $hasBranch{$temp} = 1;
    }
  }
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

if ($today_yday)
{
  getOneDay(0);
  getOneDay(1);
}
else
{
  getOneDay($daysAgo);
}

sub getOneDay {

my $daysAgo = $_[0];
$popupText = strftime "Results for %m/%d/%Y\n",
  localtime( time() - 86400 * $daysAgo );

my $r;
my $thisLog = "";
my $cmdBase = "git log";
my $since =
  $daysAgo
  ? sprintf( "--since=\"%d days ago %02d:00\" --until=\"%d days ago %02d:00\"",
  $daysAgo, $hours_before, $daysAgo - 1, $hours_after )
  : sprintf("--since=\"%02d:00:00\"", $hours_before);    #yes, git log accepts "1 days ago" which is nice

print "Running on all dirs: $cmdBase ... $since\n";
print "-ns to remove logs\n" if $showLog && !$debug;

my $branch = "main";
my $subdir = "";

for $r (@repos) {
  $branch = $allBranches ? "" : "main";
  $subdir = $r;
  if ( $r =~ /\// ) {
    my @ary = split( /\//, $r );
    $subdir = $ary[0];
    $branch = "$ary[1] --not main";
  }
  my $cmd = "$cmdBase $branch $since";
  chdir("$ghBase\\$subdir") or do { warn "fail $ghBase\\$subdir"; next; };

  my $git_branch = `git branch --list master`;
  if (($branch eq "main") && ($git_branch =~ /master/)) {
    print("Repo $r may wish to change master to main.\n");
	if (!$show_master_main) {
	  $show_master_main = 1;
	  show_shift_branch_name($r);
	}

	$branch = "master";
	next;
  }

  # `git checkout main`;
  $thisLog = `$cmd`;
  if ( ( $hasBranch{$r} ) && ( $branch eq "main" ) ) {
    print "Checking $r\'s branches:\n" if $debug;
    $cmd = "$cmdBase $since";
    my $res2 = `$cmd`;
    if ( $res2 ne $thisLog ) {
      print "WARNING: $r repo has non-main change.\n";
    }
  }
  print getcwd() . ": $cmd\n" if $debug;
  print cutDown( $thisLog, "$r/$branch" ) if $debug || $showLog;
  ( my $rbase = $r ) =~ s/\/.*//;

  # print "$r $rbase\n";
  $popupText .= "WARNING: $r is doublecounted.\n"
    if ( $count{$rbase} && $allBranches );
  $count{$r} = () = $thisLog =~ /([\n]|^)commit/gi;
  $repoSum{ $repo{$r} } += $count{$r};
}

my $lastRepo = "";

for my $k ( sort { $repo{$a} cmp $repo{$b} || $a cmp $b } keys %count ) {
  if ( $count{$k} ) {
    if ( $repo{$k} ne $lastRepo ) {
      $popupText .= "        ========$repo{$k}========\n";
      $lastRepo = $repo{$k};
    }
    $popupText .= "====$k: $count{$k}\n";
  }
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
        . ( join( ", ", @{ $siteArray{$k} } ) ) . ")\n\n";
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

}

#######################################
#subroutines

sub cutDown {
  my @x      = reverse( split( /\n/, $_[0] ) );
  my $count  = 0;
  my $c      = 1;
  my $retVal = ( $debug || $_[0] ? "======$_[1] summary\n" : "" );
  my $temp;
  my $need_header = 1;
  while ( $count <= $#x ) {
    if ( $x[$count] =~ /^Date/ ) {
      ( $temp = $x[$count] ) =~ s/^Date/'Date ' . ($c+1)/e;
	    $c++;
		$need_header = 1;

# note if we want to include the date we may need serious shuffling. This code is doing nothing at the moment.
# the 'reverse' put the date after the commit message which makes things tricky

      #$retVal .= "$temp\n";
    }
    elsif ( $x[$count] =~ /^    /  && ($x[$count] =~ /[a-z]/i)) {
      ( $temp = $x[$count] ) =~ s/^ +/($need_header ? 'Change ' : '       ') . $c . ': '/e;
      $retVal .= "$_[1] $temp\n";
	  $need_header = 0;
    }
    $count++;

    # $retVal .= ( $debug ? "$x[2+$c*6]\nC" : "$_[1] c" );
  }

  return $retVal;
}

sub hrnorm {
  die("Need something between -23 and 23. You have $_[0].") if ($_[0] > 23) || ($_[0] < -23);
  return ($_[0] + 24) % 24;
}

sub show_shift_branch_name {
  print("git branch -m master main\n");
  print("git push -u origin main\n");
  print("echo CHANGE DEFAULT BRANCH\n");
  print("https://github.com/andrewschultz/$_[0]/settings/branches\n");
  print("https://bitbucket.com/andrewschultz/$_[0]/admin\n");
  print("DONT QUITE git push origin --delete master\n");
}

sub usage {
  print <<EOT;
==========basic usage==========
-ab all branches
-nw/nmw (no) main warnings
-c open this source
-d debug (or detail, to see log details)
-sl show only log details default=$showLog, -ns/-nsl = don't show
-p pop up results
-h# = number of the hour to tweak, ha/hb=after/before norms
-[es] open site file
-m/mm shows how to switch from "master" to "main"
-u run unch.pl afterwards
-v verbose (shows commands etc.)
-(#) how many days back (default = 0, today)
EOT
  exit();
}
