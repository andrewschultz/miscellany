######################################################################
# Nitely.pl
# does nightly build/check of my (major in-progress) projects
#
# usage nitely.pl -a (for Alec and Stale Tales Slate, the active ones)
# nitely.pl -aa (for *everything*)
# nitely.pl -e to edit the TXT file

use Win32;
use POSIX qw(strftime);

use File::stat;
#use Time::localtime;

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
my %long;
my $before;

my $nmain = "c:/writing/scripts/nitely.txt";
my $npriv = "c:/writing/scripts/nitely-pr.txt";

my @projs = ();
my $proj;
my $nitedir = "c:/nightly";
my $errFile = "$nitedir/errs.htm";

projMap($nmain);
projMap($npriv);
getArgs();

chdir("$nitedir");

open(C, ">$errFile");
print C "<html><title>Total errors</title><body><center><font size=+4>TOTAL ERRORS</font><br \/><table border=1><tr><td>Test Name</td><td>Failures allowed</td><td>Failures</td><td>Passes</td><td>Comments</td></tr>\n";

for $proj (@projs)
{
  runProj($proj);
}

print C "</table>$succString$linkBack</center></body></html>";
close(C);
if ($anyTestsRun) { ffox("$errFile"); } else { print "No tests run, so I'm not showing the log file.\n"; }

my $boxMsg = "";

if ((!$quiet) && ($anyTestsRun)) { Win32::MsgBox("$boxMsg"); }

sub projMap
{
  my $longStr = "";
  my $curLong = "";
  my $curProj = "";
  open(A, "$_[0]") || die ("No $_[0]");

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
	  $long{$curProj} = $curLong;
	  next;
	}
	if ($a =~ /^D:/i) { $a =~ s/^d://gi; if (-M $a < 1.01) { $a = <A>; $cmd{$curProj} .= "$a"; } next; }
	if ($a =~ /^x/i)
	{
	  while ($a =~ /[a-z]/i)
	  {
	    $a = <A>;
		#print "Skipping $a";
      }
      next;
	}
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
  my $x = "$nitedir/$_[0].htm";
  my $y = "$nitedir/$_[0].txt";
  open(B, ">$y"); print B $_[1]; close(B);
  my @c;
  my $thisfail = 0;
  my $thiswarn = 0;
  my $thissucc = 0;
  my $bkgd;

  my @parseAry = split(/\n/, $_[1]); if ($#parseAry == -1) { print ("$_[0] had nothing to parse in the log array.\n"); return; }

  $linkBack .= "<br /><a href=\"$_[0].htm\">$_[0].htm</a> / <a href=\"$_[0].txt\">$_[0].txt</a>\n";

  $anyTestsRun = 1;

  open(B, ">$x");
  my $time = strftime "%Y-%m-%d %H:%M:%S", localtime();

  print B sprintf("<html><title>$_[0] Test Results</title><body><center><font size=+4>TEST RESULTS FOR %s at $time</font><br \/><table border=1><tr><td>Test Name</td><td>Failures allowed</td><td>Failures</td><td>Passes</td><td>Comments</td></tr>\n", defined($long{$_[0]}) ? $long{$_[0]} : $_[0]);
  for $a (@parseAry)
  {
    if ($a =~ /^TEST ?RESULT(S?):/)
    {
	  my $printErr = 1;
	  $b = $a; $b =~ s/.*RESULT(S?)://; @c = split(/,/, $b);
	  print "@c from $b\n";
	  if ($c[1] !~ /^[0-9]/) { $bkgd = $c[1]; $c[1] = "N/A"; if (!$c[4]) { $c[4] = "TEST NOT RUN"; } }
	  elsif ($c[2] == 0) { $bkgd = "green"; $printErr = 0; $thissucc++; }
	  elsif ($c[2] <= $c[1]) { $bkgd = "yellow"; $thiswarn++; }
	  else { $bkgd = "red"; $thisfail++; }
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
  if (($thisfail + $thiswarn > 0) || ($showSuccesses))
  {
    ffox($x);
  }
  else
  {
    $succString .= "<br>$_[0] passed all tests\n";
  }
}

sub opoNightly
{
my $q;
my $outfile = "$nitedir/opolis-latest.txt";
my $datefile = strftime "$nitedir/opolis-errs-%m-%d-%Y.txt", localtime();

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
	  /^-?\/$/ && do { printAvailFiles(); exit; };
	  /^-?\?$/ && do { usage(); exit; };
	  /^-?a$/ && do { @raw = ("gen", "as", "sts", "wri", "lim"); $count++; next; }; # -opo is inactive, limericks are separate from writing now
	  /^-?aa$/ && do { for $x (sort keys %cmd) { push(@raw, $x); } $count++; next; };
	  /^-?b$/ && do { $build = 1; $count++; next; };
	  /^-?d$/ && do { $debug = 1; $count++; next; };
	  /^-?e$/ && do { `$nmain`; exit; };
	  /^-?p$/ && do { `$npriv`; exit; };
	  /^-?f$/ && do { $force = 1; $count++; next; };
	  /^-?h$/ && do { `$nitedir/errs.htm`; exit; };
	  /^-?jr$/ && do { $justRelease = -1; $count++; next; };
	  /^-?n(b?)$/ && do { $build = -1; $count++; next; };
	  /^-?w$/ && do { $quiet = 1; $count++; next; };
	  /^-?s$/ && do { $showSuccesses = 1; $count++; next; };
	  /^-?q$/ && do { $build = -1; my @mylist = split(/,/, $b); for $x (@mylist) { push(@raw, $x) } $count += 2; next; };
	  /^-?t$/ && do { my @mylist = split(/,/, $b); for $x (@mylist) { push(@raw, $x) } $count += 2; next; };
	  if (-f "c:\\nightly\\$a.htm") { `"$nitedir\\$a.htm"`; exit(); }
	  if (-f "c:\\nightly\\$a.txt") { `"$nitedir\\$a.txt"`; exit(); }
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

sub printAvailFiles
{
  my @txt = ();
  my @htm = ();

  opendir(DIR, "c:\\nightly");

  my @dir = readdir(DIR);

  for (@dir)
  {
    if ($_ =~ /txt$/i) { push(@txt, $_); next; }
    if ($_ =~ /htm$/i) { push(@htm, $_); next; }
  }

  print "TXT: " . join(", ", @txt) . "\n";
  print "HTM: " . join(", ", @htm) . "\n";
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
-p = edit the private nightly test file
-f = force a nightly check even if there haven't been any daily changes
-h = open HTML file
-b = force a build (individual projects turn it off and on: on for Alec, off for Stale Tales Slate, off for opolis)
-jr = only release
-nb = force no build
-t (comma list) = projects with commas. OPO=3d+4d, AS=PC+SC, STS+SA+ROI+ANA
-a = all major projects (STS, AS and OPO)
-aa = all projects in nitely.txt (includes EctoComp, for instance)
-w = no pop-up windows box on finish
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

sub ffox
{
  system("\"$_[0]\"");
}
