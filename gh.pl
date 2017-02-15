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

my %repls;
my %repl2;

my $alph = 1;
my $procString = "";
my $defaultString;
my $testResults = 0;
my $runTrivialTests = 0;
my $byFile = 0;
my $removeTrailingSpace = 0;

my $reverse = 0;

my $ght = "c:\\writing\\scripts\\gh.txt";
my $ghp = "c:\\writing\\scripts\\gh-private.txt";
my $ghs = "c:\\writing\\scripts\\gh.pl";
my $ghreg = "c:\\writing\\scripts\\gh-reg.txt";

my %gws;
my %gwt;

preProcessHashes($ght);
preProcessHashes($ghp);

#these can't be changed on the command line. I'm too lazy to write in command line parsing right now, so the
my $justPrint = 0;
my $verbose = 0;
my $myBase = "";

my $globalTS = 0;
my $globalWarnings = 0;
my $globalStrict = 0;

my $copyAuxiliary = 0;
my $copyBinary = 0;

my $gh = "c:\\users\\andrew\\Documents\\github";
my $count = 0;
my $a;
my $a2;
my %altHash, my %do, my %poss, my %postproc;
my $np = "\"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"";

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  $a2 = lc($a);
  for ($a2)
  {
  /^gh\.pl/ && do { print "############################OOPS! You added the app name.\n"; $count++; next; };
  /^(-p|p)$/ && do { print "Opening private file, -e opens external .txt file, -c opens code file.\n"; system("start \"\" $np $ghp"); exit; };
  /^(-e|e)$/ && do { print "Opening external file, -c opens code, -p opens private file.\n"; system("start \"\" $np $ght"); exit; };
  /^(-c|c)$/ && do { print "Opening code, -e opens external .txt file, -p opens private file.\n"; system("start \"\" $np $ghs"); exit; };
  /^-?(ec|ce)$/ && do
  {
    print "Opening code/external.\n";
	system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ghs");
	system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ght");
	exit;
  };
  /^-?j$/i && do { $justPrint = 1; $count++; next; };
  /^-?f$/i && do { $byFile = 1; $count++; next; };
  /^-?v$/i && do { $verbose = 1; $count++; next; };
  /^-?rt$/i && do { $runTrivialTests = 1; $count++; next; };
  /^-?nrt$/i && do { $runTrivialTests = -1; $count++; next; };
  /^-?rts$/i && do { $removeTrailingSpace = 1; $count++; next; };
  /^-?(sw|ws)(t)?/i && do
  {
    readReplace();
	strictWarn($ght);
	strictWarn($ghp);
	if ($a =~ /t/)
	{
	printf("TEST RESULTS: strict-warn,%d,0,0,gh.pl -sw(t),%s\n", (scalar keys %gws), join("<br />", %gws));
	printf("TEST RESULTS: trailing-space,%d,0,0,gh.pl -sw(t),%s\n", (scalar keys %gwt), join("<br />", %gwt));
	}
	else
	{
	print "Total warnings needed $globalWarnings total strict needed $globalStrict total excess tab files $globalTS\n";
	}
	exit();
  };
  /^-?t$/i && do { $testResults = 1; $count++; next; };
  /^-?a$/i && do { $copyAuxiliary = 1; $count++; next; };
  /^-?b$/i && do { $copyBinary = 1; $count++; next; };
  /^-?(d|ab|ba)$/i && do { $copyBinary = 1; $copyAuxiliary = 1; $count++; next; };
  /^-?reverse$/i && do { $reverse = 1; $count++; next; };
  /^[a-z34]/i && do
  {
    if ($a2 =~ /-$/) { $a2 =~ s/-$//g; if ($altHash{$a2}) { $postproc{$altHash{$a2}} = 0; } else { $postproc{$a2} = 0; } } # sc- means you don't run trivials
    if ($a2 =~ /=$/) { $a2 =~ s/=$//g; if ($altHash{$a2}) { $postproc{$altHash{$a2}} = 1; } else { $postproc{$a2} = 1; } } # sc= means you do run trivials
    if ($altHash{$a2})
	{
	  print "$a2 => $altHash{$a2}\n";
	  $procString .= ",$altHash{$a2}";
	}
	else
	{
	  $procString .= ",$a2";
	}
	$count++;
	next;
  };
  /^-\?/ && do { usage(); };
  print "$a2 not recognized.\n";
  usage();
  }
}

if (!$procString) { $procString = $defaultString; print "Using default string: $procString\n"; }
$procString =~ s/^,//;

findTerms($ght);
findTerms($ghp);

my @procAry = split(/,/, $procString);

fillProc();

if ($verbose)
{
for my $k (sort keys %poss) { if ($k =~ /,/) { print "$k is a valid key and maps to multiple others.\n"; } else { print "$k is a valid key.\n"; } }
}

readReplace();

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
  my $temp;
  my %copto;

  for my $thisFile (@_)
  {
  open(A, $thisFile) || die ("No $thisFile");
  while ($a = <A>)
  {
    chomp($a);
    my $b = $a;
	$maxSize = 0;

	if ($a !~ /[a-z]/) { $dirName = ""; }

    if ($a =~ /^#/) { next; }
	if ($a =~ / sz:/) { $maxSize = $a; $maxSize =~ s/.* sz://g; $a =~ s/ sz:.*//g; }
	if ($a =~ /^>/)
	{
	  if ($runTrivialTests == -1) { $warnCanRun = 1; next; }
	  $b =~ s/^>//g; $b =~ s/=.*//g;
	  if (!hasHash($b)) { next; }
	  if (($runTrivialTests == 1) || ($postproc{$b})) # this is about running commands. Now the loop below should hit the FROMBASE= etc first
	  {
	  $b = $a; $b =~ s/.*=//g;
	  $b = rehash($b);
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
	 if ($a =~ /FROMBASE=/) { $temp = $a; $temp =~ s/^FROMBASE=//g; $repl2{"fromBase"} = $temp; }
	 if ($a =~ /TOBASE=/) { $temp = $a; $temp =~ s/^TOBASE=//g; $repl2{"fromShort"} = $repl2{"toBase"} = $temp; }
	 if ($a =~ /FROMSHORT=/) { $temp = $a; $temp =~ s/^FROMSHORT=//g; $repl2{"fromShort"} = $temp; }
	 if ($a =~ /POSTPROC=/i) { $a =~ s/^POSTPROC=//g; my @as = split(/,/, $a); for (@as) { $postproc{$_} = 1; } }

    $b =~ s/=.*//g;
    if (hasHash($b))
    {

	  $didOne = 1; my $wc = "";
      my $c = $a; $c =~ s/.*=//g;

	  #print "Before $c\n";
	  $c = rehash($c);
	  #print "After $c\n";

	  @d = split(/,/, $c); if ($#d == 0) { push(@d, ""); }
	  my $fromFile = $d[0];
	  my $toFile = $d[1];
	  my $short = $fromFile;
	  $short =~ s/.*[\\\/]//g;

	  if ($fromFile !~ /:/) { $fromFile = "$repl2{fromBase}\\$fromFile"; }
	  if ($repl2{"toBase"}) { $toFile = "$repl2{toBase}"; if (defined($d[1])) { $toFile .= "\\$d[1]"; } }

	  if ((! -f $fromFile) && ($fromFile !~ /\*/))
	  {
	    print "Oops $fromFile can't be found.\n";
		$badFileList .= "($.) $fromFile\n"; $badFileCount++; next;
      }

	  if ($toFile) { $dirName = $toFile; } elsif (!$dirName) { die("Need dir name to start a block of files to copy."); } else  { print"$fromFile has no associated directory, using $dirName\n"; }

	  if (-d "$gh\\$toFile") { $outName = "$gh\\$toFile\\$short"; } else { $outName = "$gh\\$toFile"; }
	  if (compare($fromFile, "$outName"))
	  {
	  if (($maxSize) && (-s $fromFile > $maxSize)) { print "Oops $fromFile size is above $maxSize.\n"; $badFileList .= "($.) (too big) $fromFile\n"; $badFileCount++; next; }
	  my $thisWild = 0;
      my $cmd = "copy \"$fromFile\" \"$gh\\$toFile\"";
	  if (($copto{$toFile}) && (! -d "$gh\\$toFile"))
	  {
	    print "Warning! Copying two different files to the same location $gh\\$toFile (next is $fromFile). Check gh*.txt or create a directory.\n";
	  }
	  $copto{$toFile}++;
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
		  #print "WILDCARD COPY: $cmd\n";
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
	    if (shouldCheck($fromFile))
		{
        checkWarnings($fromFile, 1);
		}
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
    my $q = join("/", @procAry);
    @procAry = checkForFile($ght, $ghp);
    if ($#procAry == -1) { print "Nothing found for $q.\n"; exit(); }
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

sub readReplace
{
  my $line;
  open(A, $ghreg) || die("Can't open regular expression replacement file.");
  while ($line = <A>)
  {
    if ($line =~ /^;/) { last; }
    chomp($line);
	my @lines = split(/\t/, $line);
	$repls{$lines[0]} = $lines[1];
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
  my $stillChange = 1;
  my $d;

  for (@procAry)
  {
    $do{$_} = 1;
	if ($_ eq "-a") { $alph = 1; }
  }
  while ($stillChange)
  {
    $stillChange = 0;
    for $d (keys %do)
    {
      if ($altHash{$d})
      {
        #print "$d => $altHash{$d}\n";
	    if ($altHash{$d} !~ /,/)
		{
		if (!defined($do{$altHash{$d}})) { $stillChange = 1; }
        $do{$altHash{$d}} = 1;
		}
		else
		{
		  my @alts = split(/,/, $altHash{$d});
		  for my $al (@alts)
		  {
            if (!defined($do{$altHash{$al}})) { $stillChange = 1; }
            $do{$altHash{$al}} = 1;
		  }
		}
      }
    }
  }
  for $d (keys %do)
  {
    if ($d =~ /,/) { delete($do{$d}); print "Deleted $d\n"; }
	elsif ($altHash{$d})
	{
	  delete($do{$d});
	  #print "Zapped reference $d\n";
    }
	else { print "Running $d\n"; }
  }
}

sub strictWarn
{
  my $temp;
  open(A, "$_[0]") || die;
  my $line;
  while ($line = <A>)
  {
    chomp($line);
	 if ($line =~ /FROMBASE=/) { $temp = $line; $temp =~ s/^FROMBASE=//g; $repl2{"fromBase"} = $temp; next; }
	 if ($line =~ /TOBASE=/) { $temp = $line; $temp =~ s/^TOBASE=//g; $repl2{"fromShort"} = $repl2{"toBase"} = $temp; next; }
	 if ($line =~ /FROMSHORT=/) { $temp = $line; $temp =~ s/^FROMSHORT=//g; $repl2{"fromShort"} = $temp; next; }
	 if ($line !~ /=/) { next; }
	 if ($line =~ /^[>#]/) { next; }
	 $line =~ s/.*=//;
	 $line =~ s/,.*//;
	 $line = rehash($line);
	 if ($line !~ /^c:/)
	 {
	   $line = $repl2{"fromBase"} . "\\$line";
	   #print "$line\n";
     }
	 if (shouldCheck($line)) { checkWarnings($line, 0); }
  }
  close(A);
}

###############file name, force remove trailing space
sub checkWarnings
{
  my $gotWarnings = 0;
  my $gotStrict = 0;
  my $trailingSpace = 0;
  my $numLines;

  my $line2;

  print "$_[0]\n";
  open(B,   $_[0]) || do { print "No $_[0], returning.\n"; return; };

  while ($line2 = <B>)
  {
    chomp($line2);
	if ($line2 =~ /[\t ]+$/) { $trailingSpace++; }
    if ($line2 eq "use warnings;") { $gotWarnings++; }
    if ($line2 eq "use strict;") { $gotStrict++; }
  }
  $numLines = $.;
  close(B);

  if (($removeTrailingSpace || $_[1]) && ($trailingSpace > 0)) { print "$trailingSpace trailing spaces in $_[0].\n"; $globalTS++; }
  if ($_[0] =~ /\.pl$/i)
  {
  if (!$gotStrict && $gotWarnings) { print "Need strict in $_[0] ($numLines)\n"; $globalStrict++; }
  if (!$gotWarnings && $gotStrict) { print "Need warnings in $_[0] ($numLines)\n"; $globalWarnings++; }
  if (!$gotWarnings && !$gotStrict) { print "Need warnings/strict in $_[0] ($numLines)\n"; $globalWarnings++; $globalStrict++; }
  if ($gotWarnings || $gotStrict) { $gws{$_[0]} = 1; }
  }
  if ($trailingSpace)
  {
    $gwt{$_[0]} = 1;
	if ($removeTrailingSpace || $_[1])
	{
      my $tempfile = "c:\\writing\\scripts\\temp-perl.temp";
	  open(F1, "$_[0]");
	  open(F2, ">$tempfile");
	  my $l;
	  while ($l = <F1>)
	  {
	    $l =~ s/[ \t]*$//;
		print F2 $l;
	  }
	  close(F1);
	  close(F2);
	  `copy \"$tempfile\" \"$_[0]\"`;
	  #die("copy \"$tempfile\" \"$_[0]\"");
	}
  }
}

sub rehash
{
  my $temp = $_[0];
  for my $repl (sort keys %repls)
  {
  #print "$repl $repls{$repl}\n";
  $temp =~ s/\$$repl/$repls{$repl}/g;
  }
  for my $repl (sort keys %repl2)
  {
  #print "$repl $repl2{$repl}\n";
  $temp =~ s/\$$repl/$repl2{$repl}/g;
  }
  if ($temp =~ /$$/)
  {
    print "WARNING $_[0] -> $temp still has $$ in it.\n";
  }
  return $temp;
}

sub shouldCheck
{
  if ($_[0] =~ /\.(pl|txt|c|cpp|ahs|nmr)$/i) { return 1; }
  return 0;
}

sub usage
{
print<<EOT;
========USAGE
-e edits gh.txt
-c edits gh.pl
-p edits private file
-v = verbose output
-rt/-nrt = flag running trivial tests
-j = just print commands instead of executing
-t = print various test results
-a = copy auxiliary files, -d = copy binary files, -d/ab/ba = -a + -b (eg both)
-f doesn't look for a whole project but rather for a specific file, then runs that project
-sw/ws = search for need strict/warnings
Putting = after a command runs tests
-? = this
EOT
exit;
}