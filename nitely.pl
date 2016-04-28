######################################################################
# Nitely.pl
# does nightly build/check of my (major in-progress) projects
#
# usage nitely.pl -a (for Alec and Stale Tales Slate and -opolis, the active ones)
# nitely.pl -aa (for *everything*)
# nitely.pl -e to edit the TXT file

use Win32;
use POSIX qw(strftime);

use File::stat;
use Time::localtime;

use warnings;
use strict;

#########################
#change this to debug if anything goes wrong
my $debug = 0;

my $linkBack = "";
my $succString = "";
my $justRelease = 0;
my $showSuccesses = 0;
my $anyTestsRun = 0;
my $alec = 0;
my $force = 0;
my $sts = 0;
my $build = 0;
my $opo = 0;
my $quiet = 0;
my %cmd;
my %subs;
my $before;

my @projs = ();
my $proj;
my $errFile = "c:/writing/dict/nightly/errs.htm";

print "NOTE: To run from the command line, schtasks /Run /TN \"Nightly Build\"\n";

projMap();
getArgs();

chdir("c:/writing/dict/nightly");

open(C, ">$errFile");
print C "<html><title>Total errors</title><body><center><font size=+4>TOTAL ERRORS</font><br \/><table border=1><tr><td>Test Name</td><td>Failures allowed</td><td>Failures</td><td>Passes</td><td>Comments</td></tr>\n";

for $proj (@projs)
{
  runProj($proj);
}

print C "</table>$succString$linkBack</center></body></html>";
close(C);
if ($anyTestsRun) { `$errFile`; } else { print "No tests run, so I'm not showing the log file.\n"; }

my $boxMsg = "";

if ((!$quiet) && ($anyTestsRun)) { Win32::MsgBox("$boxMsg"); }

sub projMap
{
  my $longStr = "";
  my $curLong = "";
  my $curProj = "";
  open(A, "c:/writing/dict/nitely.txt");

  while ($a = <A>)
  {
    chomp($a);
	if ($a =~ /^#/) { next; }
    if ($a =~ /~/)
	{
	  my @b = split(/~/, $a);
	  printDebug ("$b[0] ~~ $b[1]\n");
	  $subs{$b[0]} = $b[1];
	  next;
	}
	if ($a =~ /=/)
	{
	  my @b = split(/=/, $a);
	  $curProj = $b[0];
	  $curLong = $b[1];
	  next;
	}
	if ($a =~ /^D:/i) { $a =~ s/^d://gi; if (-M $a < 1.01) { $a = <A>; $cmd{$curProj} .= "$a"; } next; }
	if ($a =~ /^>/)
	{
	  $a =~ s/^>//g;
	  $longStr = "c:/games/inform/$curLong.inform/Source";
	  $a =~ s/\$\$/$curProj/g;
	  $a =~ s/\$l/$curLong/g;
	  $a =~ s/\$d/$longStr/g;
	  if ($cmd{$curProj}) { $cmd{$curProj} .= "\n"; }
	  $cmd{$curProj} .= $a;
	  #print "Command: $a\n";
	  printDebug("$curProj added command $a.\n");
	  next;
	}
	elsif ($a =~ />/)
	{
	  my @b = split(/>/, $a);
	  my $cmd = <A>;
	  if (-M "$b[0]" < -M "$b[1]")
	  {
	  if ($cmd{$curProj}) { $cmd{$curProj} .= "\n"; }
	  $cmd{$curProj} .= $cmd;
	  } else
	  {
	    printDebug("Skipping $cmd\n");
	  }
	}
  }
}

sub printDebug
{
  if ($debug) { print "$_[0]"; }
}

sub runProj
{
  $before = time();
  my $logtext = "";
  if (!$cmd{$_[0]}) { print "$_[0] had no associated project/folder.\n"; return; }
  print "Running $_[0].\n";
  my @cmds = split(/\n/, $cmd{$_[0]});
  for (@cmds)
  {
    print "RUNNING $_\n";
	if (!blockBuild($_))
	{
	$logtext .= `$_`;
	}
  }
  procIt($_[0], $logtext);
}

sub blockBuild # may be expanded to blockActivity
{
  if ($_ !~ /icl.pl/i) { return 0; }
  if ($build == -1) { return 1; }
  if ($justRelease)
  {
    if ($_ =~ /-jr/) { return 0; } else { return 1; }
  }
  return 0;
}

sub procIt
{
  my $x = "c:/writing/dict/nightly/$_[0].htm";
  my $y = "c:/writing/dict/nightly/$_[0].txt";
  open(B, ">$y"); print B $_[1]; close(B);
  my @c;
  my $thisfail = 0;
  my $thiswarn = 0;
  my $thissucc = 0;
  my $bkgd;

  my @parseAry = split(/\n/, $_[1]); if ($#parseAry == -1) { print ("$_[0] had nothing to parse in the log array.\n"); return; }
  
  $linkBack .= "<br /><a href=\"$_[0].htm\">$_[0].htm</a>\n";

  $anyTestsRun = 1;

  open(B, ">$x");
  print B "<html><title>$_[0] Test Results</title><body><center><font size=+4>TEST RESULTS FOR $_[0]</font><br \/><table border=1><tr><td>Test Name</td><td>Failures allowed</td><td>Failures</td><td>Passes</td><td>Comments</td></tr>\n";
  for $a (@parseAry)
  {
    if ($a =~ /^TEST ?RESULT(S?):/)
    {
	  my $printErr = 1;
	  $b = $a; $b =~ s/.*RESULT(S?)://; @c = split(/,/, $b);
	  print "@c from $b\n";
	  if ($c[2] == 0) { $bkgd = "green"; $printErr = 0; $thissucc++; } else
	  {
	    if ($c[2] < 0) { $bkgd = "grey"; $thisfail++; } elsif ($c[2] <= $c[1]) { $bkgd = "yellow"; $thiswarn++; } else { $bkgd = "red"; $thisfail++; }
	  }
	  my $myLine = "<tr><td bgcolor=$bkgd>" . join ("</td><td>", @c) . "</td></tr>\n";
	  print B $myLine;
	  if ($printErr) { print C $myLine; }
	}
  }
  print B "</table border=1></center>\n";
  print B "<center><font size=+3>$thisfail failures, $thiswarn warnings, $thissucc successes.</font><br \/>\n";
  my $secs = time() - $before;
  print B $secs . " seconds taken.";
  print B "</center>\n</body></html>";
  close(B);
  if (($thisfail + $thiswarn > 0) || ($showSuccesses)) { `$x`; } else { $succString .= "<br>$_[0] passed all tests\n"; }
}

sub opoNightly
{
my $q;
my $outfile = "c:/writing/dict/nightly/opolis-latest.txt";
my $datefile = strftime "c:/writing/dict/nightly/opolis-errs-%m-%d-%Y.txt", localtime;

my $threed = "c:/games/inform/threediopolis.inform/source/story.ni";
my $fourd = "c:/games/inform/fourdiopolis.inform/source/story.ni";

my $mod3 = (-M "$threed") < 1;
my $mod4 = (-M "$fourd") < 1;

if ($mod3 || $mod4 || $force)
{
open(OUTFILE, ">$outfile");
printboth("Source code checking:");
sourceCheck("threediopolis");
sourceCheck("fourdiopolis");
$boxMsg .= "Results in $outfile or $datefile.\n";
close(OUTFILE);
}
else
{
$boxMsg .= "No Opolis files modified in the last day.\n"; return;
}

procIt($outfile);
}

###################################
#this gets the arguments and interprets them.
#
sub getArgs
{
  my $a, my $b;
  my $x;
  my $count = 0;
  my @raw = ();
  while ($count <= $#ARGV)
  {
    $a = $ARGV[$count];
	if ($count <= $#ARGV) { $b = $ARGV[$count+1]; } else { $b = ""; }
	for ($a)
	{
	  /^-?\?$/ && do { usage(); exit; };
	  /^-a$/ && do { @raw = ("opo", "as", "sts"); $count++; next; };
	  /^-aa$/ && do { for $x (sort keys %cmd) { push(@raw, $x); } $count++; next; };
	  /^-b$/ && do { $build = 1; $count++; next; };
	  /^-d$/ && do { $debug = 1; $count++; next; };
	  /^-?e$/ && do { `c:/writing/dict/nitely.txt`; exit; };
	  /^-f$/ && do { $force = 1; $count++; next; };
	  /^-?h$/ && do { `c:/writing/dict/nightly/errs.htm`; exit; };
	  /^-jr$/ && do { $justRelease = -1; $count++; next; };
	  /^-nb$/ && do { $build = -1; $count++; next; };
	  /^-q$/ && do { $quiet = 1; $count++; next; };
	  /^-s$/ && do { $showSuccesses = 1; $count++; next; };
	  /^-t$/ && do { my @mylist = split(/,/, $b); for $x (@mylist) { push(@raw, $x) } $count += 2; next; };
	  print "Invalid flag $a specified.\n";
	  usage();
	}
  }
  for my $k (@raw)
  {
    my $zz;
    if ($subs{$k})
	{
	  my @plist = split(/,/, $subs{$k});
	  for $zz (@plist) { push(@projs, $zz); }
	} else { push(@projs, $k); }
  }
}

sub openLatest
{
`c:\\writing\\dict\\nightly\\$_[0]-latest.txt`;
}

######################################################
#basic usage stuff
#
sub usage
{
print <<EOT;
-d = debug
-e = edit the nightly test text file
-f = force a nightly check even if there haven't been any daily changes
-h = open HTML file
-b = force a build (individual projects turn it off and on: on for Alec, off for Stale Tales Slate, off for opolis)
-jr = only release
-nb = force no build
-t (comma list) = projects with commas. OPO=3d+4d, AS=PC+SC, STS+SA+ROI+ANA
-a = all major projects (STS, AS and OPO)
-aa = all projects in nitely.txt (includes EctoComp, for instance)
-q = no pop-up windows box on finish
-s = show successes
EXAMPLES: nitely.pl -a -q
nitely.pl -nb -t sts (runs Stale Tales Slate without building)
nitely.pl -jr -t pc (runs Problems Compound only building release)
EOT
exit;
}

#########################################
#A stub to print to STDOUT and a file
#
sub printboth
{
  print "$_[0]\n";
  print OUTFILE "$_[0]\n";
  print OUTFILE "=" x 20;
  print OUTFILE "\n\n";
}

###########################################
#check for random ideas in my STS file
#
#anything below \ro3 in quotes works
#
sub newIdeas
{
  open(A, "c:/writing/dict/sts.txt") || return 0;
  while ($a = <A>)
  {
    if ($a =~ /^\"/) { close(A); return 1; }
    if ($a =~ /^\\ro3/) { close(A); return 0; }
  }

  return 0;
}
