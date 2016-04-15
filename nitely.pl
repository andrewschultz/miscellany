######################################################################
# Nitely.pl
# does nightly build/check of my (major in-progress) projects
#
# usage nitely.pl -a (for Alec and Stale Tales Slate and -opolis, the active ones)
# nitely.pl -aa (for *everything*)
# nitely.pl -e to edit the TXT file

use Win32;
use POSIX qw(strftime);

use warnings;
use strict;

#########################
#change this to debug if anything goes wrong
my $debug = 0;

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

open(C, ">$errFile");
print C "<html><title>Total errors</title><body><center><font size=+4>TOTAL ERRORS</font><br \/><table border=1><tr><td>Test Name</td><td>Failures allowed</td><td>Failures</td><td>Passes</td><td>Comments</td></tr>\n";

for $proj (@projs)
{
  runProj($proj);
}

print C "</table></center></body></html>";
close(C);
`$errFile`;

my $boxMsg = "";

if (!$quiet) { Win32::MsgBox("$boxMsg"); }

sub projMap
{
  my $longStr = "";
  my $curLong = "";
  my $curProj = "";
  open(A, "c:/writing/dict/nitely.txt");
  
  while ($a = <A>)
  {
    chomp($a);
    if ($a =~ /~/)
	{
	  my @b = split(/~/, $a);
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
	  if ($debug) { print "$curProj added command $a.\n"; }
	  next;
	}
  }
}

sub runProj
{
  $before = time();
  print "Running $_[0].\n";
  my $logtext = "";
  my @cmds = split(/\n/, $cmd{$_[0]});
  for (@cmds) { print "RUNNING $_\n"; $logtext .= `$_`; }
  procIt($_[0], $logtext);
}

sub procIt
{
  my $x = "c:/writing/dict/nightly/$_[0].htm";
  my $y = "c:/writing/dict/nightly/$_[0].txt";
  open(B, ">$y"); print B $_[1]; close(B);
  my @c;
  my $thisfail = 0;
  my $thissucc = 0;
  my $bkgd;
  
  my @parseAry = split(/\n/, $_[1]);

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
	    $thisfail++;
        if ($c[2] < 0) { $bkgd = "grey"; } elsif ($c[2] <= $c[1]) { $bkgd = "yellow"; } else { $bkgd = "red"; }
	  }
	  my $myLine = "<tr><td bgcolor=$bkgd>" . join ("</td><td>", @c) . "</td></tr>\n";
	  print B $myLine;
	  if ($printErr) { print C $myLine; }
	}
  }
  print B "</table border=1></center>\n";
  print B "<center><font size=+3>$thisfail failures, $thissucc successes.</font><br \/>\n";
  my $secs = time() - $before;
  print B $secs . " seconds taken.";
  print B "</center>\n</body></html>";
  close(B);
  `$x`;
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
  while ($count <= $#ARGV)
  {
    $a = $ARGV[$count];
	if ($count <= $#ARGV) { $b = $ARGV[$count+1]; } else { $b = ""; }
	for ($a)
	{
	  /^-?e$/ && do { `c:/writing/dict/nitely.txt`; exit; };
	  /-f/ && do { $force = 1; $count++; next; };
	  /-e/ && do { `c:/writing/dict/nitely.txt`; $count++; next; };
	  /-b/ && do { $build = 1; $count++; next; };
	  /-nb/ && do { $build = -1; $count++; next; };
	  /-aa/ && do { for $x (sort keys %cmd) { push(@projs, $x); } $count++; next; };
	  /-a/ && do { @projs = ("3d", "4d", "pc", "sc", "sa", "roi"); $count++; next; };
	  /-t/ && do { my @mylist = split(/,/, $b); for $x (@mylist) { if ($subs{$x}) { @projs = (@projs, split(/,/, $subs{$x})); } else { @projs = (@projs, $x); } } $count += 2; next; };
	  /-q/ && do { $quiet = 1; $count++; next; };
	  /-\?/ && do { usage(); exit; };
	  print "Invalid flag $a specified.\n";
	  usage();
	}
  }
}

sub openLatest
{
`c:\\writing\\dict\\nightly\\$_[0]-latest.txt`;
}

sub usage
{
print <<EOT;
-e = edit the nightly test text file
-f = force a nightly check
-b = force a build (individual projects turn it off and on: on for Alec, off for Stale Tales Slate, off for opolis)
-nb = force no build
-3|4|34 = Opolis (Threediopolis, Fourdiopolis)
-a = Alec (Slicker city, Problems Compound)
-s = Stale Tales Slate (Shuffling Around, Roiling Original)
-oa = open latest Alec file
-oa = open latest STS file
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
