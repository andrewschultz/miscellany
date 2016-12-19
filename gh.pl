############################################################
#gh.pl
#This copies over changed files to the github directory from various sources.
#It uses gh.txt.
#
#commands: gh.pl sts (stale tales slate) or gh.pl e (edit the list file)
#
# gh.pl c opens code, e opens gh.txt, p opens private file

use strict;
use warnings;

use File::Compare;

my $warnCanRun = 0;

my $alph = 1;
my $procString;
my $defaultString;
my $testResults = 0;
my $runTrivialTests = 0;
my $byFile = 0;

my $reverse = 0;

my $ght = "c:\\writing\\scripts\\gh.txt";
my $ghp = "c:\\writing\\scripts\\gh-private.txt";
my $ghs = "c:\\writing\\scripts\\gh.pl";

preProcessHashes($ght);
preProcessHashes($ghp);

#these can't be changed on the command line. I'm too lazy to write in command line parsing right now, so the
my $justPrint = 0;
my $verbose = 0;
my $myBase = "";

my $copyAuxiliary = 0;
my $copyBinary = 0;

my $gh = "c:\\users\\andrew\\Documents\\github";
my $count = 0;
my $a;
my %altHash, my %do, my %poss, my %postproc;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  for ($a)
  {
  /^(-p|p)$/ && do { print "Opening private file, -e opens external .txt file, -c opens code file.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ghp"); exit; };
  /^(-e|e)$/ && do { print "Opening external file, -c opens code, -p opens private file.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ght"); exit; };
  /^(-c|c)$/ && do { print "Opening code, -e opens external .txt file, -p opens private file.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ghs"); exit; };
  /^-?(ec|ce)$/ && do
  {
    print "Opening code/external.\n";
	system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ghs");
	system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ght");
	exit;
  };
  /^-?j$/ && do { $justPrint = 1; $count++; next; };
  /^-?f/ && do { $byFile = 1; $count++; next; };
  /^-?v$/ && do { $verbose = 1; $count++; next; };
  /^-rt$/ && do { $runTrivialTests = 1; $count++; next; };
  /^-nrt$/ && do { $runTrivialTests = -1; $count++; next; };
  /^-?t$/ && do { $testResults = 1; $count++; next; };
  /^-?a$/ && do { $copyAuxiliary = 1; $count++; next; };
  /^-?b$/ && do { $copyBinary = 1; $count++; next; };
  /^-?(d|ab|ba)$/ && do { $copyBinary = 1; $copyAuxiliary = 1; $count++; next; };
  /^-?reverse$/ && do { $reverse = 1; $count++; next; };
  /^[a-z34]/ && do
  {
    if ($a =~ /-$/) { $a =~ s/-$//g; if ($altHash{$a}) { $postproc{$altHash{$a}} = 0; } else { $postproc{$a} = 0; } } # sc- means you do run trivials
    if ($a =~ /=$/) { $a =~ s/=$//g; if ($altHash{$a}) { $postproc{$altHash{$a}} = 1; } else { $postproc{$a} = 1; } } # sc= means you do run trivials
    if ($altHash{$a})
	{
	  print "$a => $altHash{$a}\n";
	  $procString = $altHash{$a};
	}
	else
	{
	  $procString = $a;
	}
	$count++;
	next;
  };
  /^-\?/ && do { usage(); };
  print "$a not recognized.\n";
  usage();
  }
}

if (!$procString) { $procString = $defaultString; print "Using default string: $procString\n"; }

findTerms($ght);
findTerms($ghp);

my @procAry = split(/,/, $procString);

fillProc();

if ($verbose)
{
for my $k (sort keys %poss) { if ($k =~ /,/) { print "$k is a valid key and maps to multiple others.\n"; } else { print "$k is a valid key.\n"; } }
}

if (!processTerms($ght, $ghp))
{
  if ($byFile && ($#procAry > -1))
  {
  fillProc();
  processTerms($ght, $ghp);
  }
}


##########################################
#the main function

sub processTerms
{
  my @d;
  my $copies = 0; my $unchanged = 0; my $wildcards = 0; my $badFileCount = 0; my $didOne = 0; my $uncop = 0;
  my $badFileList = "";
  my $outName;
  my $quickCheck = "";
  my $fileList = "";
  my $uncopiedList = "";
  my $dirName = "";
  my $fromBase="", my $toBase="";
  my $fromShort="";
  my $maxSize = 0;
  my $wildSwipes = 0;

  for my $thisFile (@_)
  {
  open(A, $thisFile) || die ("No $thisFile");
  while ($a = <A>)
  {
    chomp($a);
    my $b = $a;
	$maxSize = 0;

    if ($a =~ /^#/) { next; }
	if ($a =~ / sz:/) { $maxSize = $a; $maxSize =~ s/.* sz://g; $a =~ s/ sz:.*//g; }
	if ($a =~ /^>/)
	{
	  if ($runTrivialTests == -1) { $warnCanRun = 1; next; }
	  $b =~ s/^>//g; $b =~ s/=.*//g;
	  if (!hasHash($b)) { next; }
	  if (($runTrivialTests == 1) || ($postproc{$b}))
	  {
	  $b = $a; $b =~ s/.*=//g;
	  #below is duplicate code but it'll do for now
	  $b =~ s/\$ws/c:\\writing\\scripts/g;
	  $b =~ s/\$tr/c:\\games\\inform\\triz\\mine/g;
	  $b =~ s/\$wd/c:\\writing\\dict/g;
	  $b =~ s/\$if/$fromBase/g;
	  $b =~ s/\$im/c:\\games\\inform\\$fromShort materials/g;
	  $b =~ s/\$is/c:\\games\\inform\\$fromShort.inform\\source/g;
	  $b =~ s/\$id/c:\\games\\inform\\$fromShort.inform\\uuid.txt/g;
	  #above is duplicate code but it'll do for now
	  $quickCheck .= `$b`;
	  }
	  else { $warnCanRun = 1; next; }
	  next;
    }
	##################note prefix like -a (auxiliary) and -b (build)
	#this is because auxiliary or binary files could be quite large
	#format is -a:
	#-b:
	my $prefix = "";
	my $c = $a; if ($c =~ /^-.:/) { $c =~ s/(^..).*/$1/g; $prefix = $c; $b =~ s/^-.://g; }
	 if ($a =~ /FROMBASE=/) { $fromBase = $a; $fromBase =~ s/^FROMBASE=//g; }
	 if ($a =~ /TOBASE=/) { $toBase = $a; $toBase =~ s/^TOBASE=//g; $fromShort = $toBase; }
	 if ($a =~ /FROMSHORT=/) { $fromShort = $a; $fromShort =~ s/^FROMSHORT=//g; }
	 if ($a =~ /POSTPROC=/i) { $a =~ s/^POSTPROC=//g; my @as = split(/,/, $a); for (@as) { $postproc{$_} = 1; } }

    $b =~ s/=.*//g;
    if (hasHash($b))
    {

	  $didOne = 1; my $wc = "";
      my $c = $a; $c =~ s/.*=//g;
	  # I could probably do the below a little more programatically but for right now this gets rid of a lot of the repetitive stuff that clogs the text files
	  $c =~ s/\$ws/c:\\writing\\scripts/g;
	  $c =~ s/\$tr/c:\\games\\inform\\triz\\mine/g;
	  $c =~ s/\$wd/c:\\writing\\dict/g;
	  $c =~ s/\$if/$fromBase/g;
	  $c =~ s/\$im/c:\\games\\inform\\$fromShort materials/g;
	  $c =~ s/\$is/c:\\games\\inform\\$fromShort.inform\\source/g;
	  $c =~ s/\$id/c:\\games\\inform\\$fromShort.inform\\uuid.txt/g;

	  @d = split(/,/, $c); if ($#d == 0) { push(@d, ""); }
	  my $fromFile = $d[0];
	  my $toFile = $d[1];
	  my $short = $fromFile; $short =~ s/.*[\\\/]//g;

	  if ($fromFile !~ /:/) { $fromFile = "$fromBase\\$fromFile"; }
	  if ($toBase) { $toFile = "$toBase\\$d[1]"; }


	  if ((! -f $fromFile)  && ($fromFile !~ /\*/)) { print "Oops $fromFile can't be found.\n"; $badFileList .= "$fromFile\n"; $badFileCount++; next; }


	  if ($toFile) { $dirName = $toFile; } elsif (!$dirName) { die("Need dir name to start a block of files to copy."); } else  { print"$fromFile has no associated directory, using $dirName\n"; }

	  if (-d "$gh\\$toFile") { $outName = "$gh\\$toFile\\$short"; } else { $outName = "$gh\\$toFile"; }
	  if (compare($fromFile, "$outName"))
	  {
	  if (($maxSize) && (-s $fromFile > $maxSize)) { print "Oops $fromFile size is above $maxSize.\n"; $badFileCount++; next; }
	  my $thisWild = 0;
      my $cmd = "copy \"$fromFile\" \"$gh\\$toFile\"";
	  if ($reverse) { if ($short =~ /\*/) { next; } $cmd = "copy \"$gh\\$toFile\\$short\" \"$fromFile\""; }
	  if ($fromFile =~ /\*/)
	  {
		my $wildYet = 0;
		my $wildFrom = $c; $wildFrom =~ s/,.*//g; $wildFrom =~ s/\\[^\\]+$//;
		my $wildCheck = $c; $wildCheck =~ s/,.*//g; $wildCheck =~ s/.*\\//; $wildCheck =~ s/\*/\.\*/g;
		opendir(DIR, "$wildFrom") || do { print "$wildFrom dir doesn't exist.\n"; next; };
		my @x = readdir(DIR);
		my @y = ();
		for (@x)
		{
		  if ($_ =~ /$wildCheck/) { push (@y, $_); }
		}
		if ($#y == -1) { print "No matches for $wildFrom/$wildCheck.\n"; next; }
		for (@y)
		{
		  if (compare("$wildFrom\\$_", "$gh\\$toFile\\$_"))
		  {
		  $cmd = "copy $wildFrom\\$_ $gh\\$toFile\\$_";
		  `$cmd`;
		  $fileList .= "$wildFrom\\$_\n";
		  #print "$cmd\n$toBase\n$toFile\n";
		  $wildcards++;
		  $copies++;
		  if (!$wildYet) { $wildYet++; $wildSwipes++; }
		  }
		}
		next;
	  }
	  if ($justPrint) { print "$cmd\n"; $fileList .= "$fromFile\n"; }
	  else
	  {
	    if (shouldRun($prefix)) { $fileList .= "$fromFile\n"; $wc = `$cmd`; if ($thisWild) { print "====WILD CARD COPY-OVER OUTPUT\n$wc"; } else { $copies++; } } else { print "$cmd not run, need to set $prefix flags.\n"; $uncopiedList .= "$fromFile\n"; $uncop++; }
      }
	  }
	  else
	  {
	  $unchanged++;
	  }
#      `$cmd`;
    }
  }
  close(A);
  }
  if (!$didOne)
  {
    @procAry = checkForFile($ght, $ghp);
  }
  else
  {
    print "Copied $copies file(s), $wildcards/$wildSwipes wild cards, $unchanged unchanged, $badFileCount bad files, $uncop uncopied files.\n";
	my $cbf = $copies+$badFileCount;
	my $proc2 = join("/", split(/,/, $procString));
	if ($testResults && $cbf)
	{
	  $fileList =~ s/\n/<br \/>/g;
	  print "TEST RESULTS:$proc2 file-copies,orange,$cbf,0,gh.pl $procString<br>$fileList\n";
	}
	if ($fileList) { print "====FILE LIST:\n$fileList"; }
	if ($uncopiedList) { print "====UNCOPIED FILES ($uncop):\n$uncopiedList"; }
	if ($badFileCount) { print "====BAD FILES ($badFileCount):\n$badFileList"; }
  }
  if ($quickCheck) { print "\n========quick verifications\n$quickCheck"; }
  if ($warnCanRun) { print "\nYou could have run code checking by tacking on an =."; }
  return $didOne;
}

##########################
# finds all valid terms in gh.txt or gh-private.txt
# not individual files, just pc, sa, etc

sub findTerms
{
open(A, $_[0]) || die ("Oops, couldn't open $_[0].");

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /~/) { next; } #congruency
  if ($a =~ /^d:/) { next; } #default
  if ($a =~ /^;/) { last; }
  if ($a =~ /^#/) { next; }
  if ($a !~ /[a-z]/i) { next; }
  $a =~ s/=.*//g;
  $poss{$a} = 1;
}

close(A);
}

###############################
# this finds similarities e.g. pc~tpc

sub preProcessHashes
{
  my $bail = 0;
  open(A, "$_[0]") || die ("Can't open $_[0].");
  while ($a = <A>)
  {
    chomp($a);
    if ($a =~ /^d:/)
	{
	  $defaultString = $a;
	  $defaultString =~ s/^d://gi;
	}
	if ($a =~ /~/)
	{
	  my @b = split(/~/, $a);
	  my @c = split(/,/, $b[0]);
	  for (@c) { if ($altHash{$_}) { print "$_ has duplicate hash: was $altHash{$_}, also found $b[1].\n"; $bail = 1; } $altHash{$_} = $b[1]; }
	  #print "@b[0] -> @b[1]\n";
	}
  }
  close(A);
  if ($bail > 0) { print "Fix duplicate hashes before continuing.\n"; exit; }
}

sub shouldRun
{
if (($_[0] =~ /^-a/) && ($copyAuxiliary)) { return 1; }
if (($_[0] =~ /^-b/) && ($copyBinary)) { return 1; }
if ($_[0] eq "") { return 1; }
return 0;
}

sub hasHash
{
  if ($do{$_[0]}) { return 1; }
  if (($altHash{$_[0]}) && ($do{$altHash{$_[0]}})) { return 1; }
  return 0;
}

sub checkForFile
{
  my $line;
  my @mb;
  my @mb2;
  my $curProj = "";
  my $last = "";
  for my $thisfi(@_)
  {
  open(A, "$thisfi");
  while ($line = <A>)
  {
    if ($line =~ /\b$procString\b/) { chomp($line); push (@mb, $line); $last = $line; $curProj = $last; $curProj =~ s/=.*//; if ($curProj ne $last) { push(@mb2, $curProj); } $last = $curProj; }
  }
  close(A);
  }
  if (($byFile == 1) && ($#mb >= 0))
  {
    return @mb2;
	exit();
  }
  if ($#mb >= 0) { print "No project found, but there are close matches you may be able to run with -f:\n" . join("\n", @mb) . "\n"; exit(); }
  return ();
}

sub fillProc
{
for (@procAry)
{
  if ($_ eq "-a")
  { $alph = 1; next; }
  if ($altHash{$_}) { $do{$altHash{$_}} = 1; print "$_ => $altHash{$_}\n"; }
  else
  {
  $do{$_} = 1;
  }
}
}

sub usage
{
print<<EOT;
========USAGE
-e edits gh.txt
-c edits gh.pl
-p edits private file
-v = verbose output
-j = just print commands instead of executing
-? = this
-a = copy auxiliary files
-b = copy binary files
-d = -a + -b (eg both)
EOT
exit;
}