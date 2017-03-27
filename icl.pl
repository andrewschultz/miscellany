#ICL = Inform Command Line
#
#Perl script to compile stuff without having to open the IDE, etc.
#
#cd c:/Users/Andrew/Documents/Inform/Extensions/
#cd c:/games/inform/$proj.inform/Build
#"C:/Program Files (x86)/Inform 7/Compilers/ni" -rules "C:/Program Files (x86)/Inform 7/Inform7/Extensions" -package "C:/games/inform/$proj.inform" -extension=ulx
#"C:/Program Files (x86)/Inform 7/Compilers/inform-633" -kwSDG +include_path=../Source,./ auto.inf output.ulx
#set HOME=c:/games/inform/$proj.inform
#"C:/Program Files (x86)/Inform 7/Compilers/ni" -release -rules "C:/Program Files (x86)/Inform 7/Inform7/Extensions" -package "C:/games/inform/$proj.inform" -extension=ulx
#"C:/Program Files (x86)/Inform 7/Compilers/cblorb" -windows Release.blurb Build/output.gblorb

#I can and should expand this to do more than one at once

use strict;
use warnings;

my %zmac;
my %proj;
my %use6l;
my %forceDir;

#######################options
my $informBase = 0;
my $informDir = 0;
my $infOnly = 0;

my $infDir;

#######################vars
my @allProj;
my @compileList;
my @inDirs;
my @defaultCompileList;

my $ex;
my $gz;
my $iflag;
my $v6l = 0;
my $bdir;
my $mat;
my $bmat;
my $i6x;

my $betaDir = "c:\\games\\inform\\beta.inform";
my $baseDir = "c:\\games\\inform";

open(X, "c:/writing/scripts/icl.txt") || die ("Need icl.txt.");

my $x; my $y;

while ($x = <X>)
{
  chomp($x);
  if ($x =~ /^;/) { last; }
  if ($x =~ /^#/) { next; }

  my @cmd = split(/=/, $x);
  if (defined($cmd[1]))
  {
    if (lc($cmd[0]) eq lc("default")) { @defaultCompileList = split(/,/, $cmd[1]); }
    elsif (lc($cmd[0] eq lc "allproj")) { @allProj = split(/,/, $cmd[1]); }
	else { my @froms = split(/,/, $cmd[0]); for (@froms) { $proj{$_} = $cmd[1]; } }
  }
  elsif ($x =~ /^FORCE /) { $y = $x; $y =~ s/^FORCE //g;  my @z = split(/=/, $y); $forceDir{$z[0]} = $z[1]; }
  elsif ($x =~ /^z:/) { $y = $x; $y =~ s/^z://g; $zmac{$y} = 1; }
  elsif ($x =~ /^6l:/) { $y = $x; $y =~ s/^6l://g; $use6l{$y} = 1; }
}
#sensible abbreviations

$use6l{"compound"} = 0;

my $runBeta = 0;
my $debug = 0;
my $release = 1;
my $execute = 0;

my $count = 0;

while ($count <= $#ARGV)
{

  $a = $ARGV[$count];
  for ($a)
  {
  #print "Argument " . ($a + 1) . " of " . ($#ARGV + 1) . ": $a\n";
  /^(b|beta)$/ && do { $runBeta = 1 - $runBeta; $count++; next; };
  /^-?jb$/ && do { $runBeta = 1; $debug = $release = 0; $count++; next; };
  /^-?jd$/ && do { $debug = 1; $runBeta = $release = 0; $count++; next; };
  /^-?jr$/ && do { $release = 1; $debug = $runBeta = 0; $count++; next; };
  /^-?f$/ && do { $release = $debug = $runBeta = 0;
    if ($a =~ /r/) { $release = 1; }
    if ($a =~ /d/) { $debug = 1; }
    if ($a =~ /b/) { $runBeta = 1; }
	$count++; next;
  };
  /^-?inf$/ && do { $infOnly = 1; $count++; next; };
  /^-?l$/ && do { $v6l = 1 - $v6l; $informDir = $inDirs[$v6l]; $count++; next; };
  /^-?ba$/ && do { $informBase = $ARGV[$count+1]; $count++; next; };
  /^-?be$/ && do { $betaDir = $ARGV[$count+1]; $count++; next; };
  /^-?nr$/ && do { $release = 0; $count++; next; };
  /^-?yr$/ && do { $release = 1; $count++; next; };
  /^-?nd$/ && do { $debug = 0; $count++; next; };
  /^-?yd$/ && do { $debug = 1; $count++; next; };
  /^-?x$/ && do { $execute = 1; $count++; next; };
  /^-?e$/ && do { `c:\\writing\\scripts\\icl.txt`; exit; };
  /^-?a$/ && do { for my $entry (@allProj) { push(@compileList, $a); } $count++; next; };
  /^-\?$/ && do { usage(); exit; };
  /^-/ && do { print "Not a valid option.\n"; usage(); exit; };
  push(@compileList, $a); $count++; next;
  }
}

if ($#compileList == -1) { print "Nothing in compile list. Using default: @defaultCompileList.\n"; @compileList = @defaultCompileList; }

my $myProj;

for my $toComp (@compileList)
{
  if ($proj{$toComp}) { $myProj = $proj{$toComp}; }
  elsif ($proj{"-$toComp"}) { $myProj = $proj{"-$toComp"}; }
  else {
  die("No project for $toComp. If you wanted an option, try -?.\n");
  }
  $infDir = $inDirs[$v6l];
  runProj($myProj);
  $count++;
}

if (-f "gameinfo.dbg") { print "Deleting .dbg file\n"; unlink<gameinfo.dbg>; }

####################################################
#subroutines
#

sub runProj
{
# this is bad coding but there's only two exceptions for now: Threediopolis and Dirk.
$ex = "ulx";
$gz = "gblorb";
$iflag = "G";
if ($zmac{$_[0]}) { $ex = "z8"; $gz = "zblorb"; $iflag = "v8"; }

if ($forceDir{$_[0]})
{
$bdir = $forceDir{$_[0]};
}
else
{
$bdir = "$baseDir\\$_[0].inform";
}

$infDir = buildDir($_[0]);
$i6x = i6exe($_[0]);

if ($runBeta)
{
  $mat = "$baseDir\\$_[0].materials";
  $bmat = "$baseDir\\beta Materials";
  if ($use6l{$_[0]}) { $mat =~ s/ materials/\.materials/g; $bmat =~ s/ materials/\.materials/g; }
  copyToBeta($bdir);
  doOneBuild($betaDir, "~D", "$baseDir\\beta Materials", "beta", "$_[0]");
}

if ($release)
{
  doOneBuild("$bdir", "~D", "$baseDir\\$_[0] Materials", "release", "$_[0]");
}

if ($debug)
{
  doOneBuild("$bdir", "D", "$baseDir\\$_[0] Materials", "debug", "$_[0]");
}

}

sub doOneBuild
{
  my $outFile = "$_[0]\\Build\\output.$ex";
  my $dflag = "$_[1]";
  my $infOut = "$_[0]\\Build\\auto.inf";

  delIfThere($infOut);

  my $compileCheck = `\"$infDir\\Compilers\\ni\" -release -rules \"$infDir\\Inform7\\Extensions\" -package \"$_[0]\" -extension=$ex"`;
  print "BUILD RESULTS\n=================\n$compileCheck";
  if ($compileCheck =~ /has finished/i)
  {
    print "TEST RESULTS:$_[4] $_[3] $_[0] i7->i6 failed,0,1,0\n";
	if (!$infOnly)
	{
    print "TEST RESULTS:$_[4] $_[3] $_[0] i6->binary untested,grey,0,0\n";
    print "TEST RESULTS:$_[4] $_[3] $_[0] blorb creation untested,grey,0,0\n";
	}
	return;
  }
  if ($infOnly) { return; }

  ####probably not necessary
  #print "TEST RESULTS:$_[4] $_[3] $_[0] i7->i6 succeeded,0,0,0\n";

  delIfThere($outFile);
  system("\"$infDir/Compilers/$i6x\" -kw~S$dflag$iflag +include_path=$_[0] $infOut $outFile");

  if (! -f $outFile)
  {
    print "TEST RESULTS:$_[4] $_[3] $_[0] i6->binary failed,0,1,0\n";
    print "TEST RESULTS:$_[4] $_[3] $_[0] blorb creation untested,grey,0,0\n";
	return;
  }

  ####probably not necessary
  #print "TEST RESULTS:$_[4] $_[3] $_[0] i6->binary succeeded,0,0,0\n";

  my $blorbFileShort = getFile("$_[0]/Release.blurb");

  if ($_[3] ne "debug") { $blorbFileShort = "$_[3]-$blorbFileShort"; }
  my $outFinal = "$_[2]\\Release\\$blorbFileShort";
  delIfThere("$outFinal");
  sysprint("\"$infDir/Compilers/cblorb\" -windows \"$_[0]\\Release.blurb\" \"$outFinal\"");

  if ((! -f $outFinal) || (-s "$outFinal" < -s "$outFile"))
  {
    print "TEST RESULTS:$_[4] $_[3] $_[0] blorb creation failed,0,1,0\n";
	return;
  }

    print "TEST RESULTS:$_[4] $_[3] $_[0] blorb creation passed,0,0,0\n";

  return;
}

sub sysprint
{
  print "$_[0]\n";
  system("$_[0]");
}

sub copyToBeta
{
print("set HOME=$betaDir\n\n");
print "****BETA BUILD****\n\n";

my $mtr = $_[0]; $mtr =~ s/\.inform/ materials/g;

system("copy $_[0]\\Release.blurb $betaDir\\Release.blurb");
system("copy $_[0]\\uuid.txt $betaDir\\uuid.txt");
system("copy $_[0]\\uuid.txt $betaDir\\uuid.txt");
system("erase \"$bmat\\Figures\"*");
system("copy \"$mtr\\Figures\\*\" \"$bmat\\Figures\"");

print "Searching for cover....\n";

my $cover = "$betaDir\\Cover";
my $covr = "$betaDir\\Release\\Cover";
my $smcov = "$betaDir\\Small Cover";
if (-f "$cover.jpg") { print "BETA: Erasing old jpg.\n"; system("Erase \"$cover.jpg\""); }
if (-f "$cover.png") { print "BETA: Erasing old png.\n"; system("Erase \"$cover.png\""); }
if (-f "$covr.png") { print "BETA: Erasing old Release\\png.\n"; system("Erase \"$covr.png\""); }
if (-f "$covr.jpg") { print "BETA: Erasing old Release\\jpg.\n"; system("Erase \"$covr.jpg\""); }
if (-f "$smcov.jpg") { print "BETA: Erasing old small jpg.\n"; system("Erase \"$smcov.jpg\""); }
if (-f "$smcov.png") { print "BETA: Erasing old small png.\n"; system("erase \"$smcov.png\""); }

if (-f "c:/games/inform/$_[0] materials/Cover.png") { print "Copying png over.\n"; system("copy \"$baseDir\\$_[0] materials\\Cover.png\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Cover.jpg") { print "Copying jpg over.\n"; system("copy \"$baseDir\\$_[0] materials\\Cover.jpg\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Small Cover.png") { print "Copying small png over.\n"; system("copy \"$baseDir\\$_[0] materials\\Small Cover.png\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Small Cover.jpg") { print "Copying small jpg over.\n"; system("copy \"$baseDir\\$_[0] materials\\Small Cover.jpg\" \"$bmat\""); }

modifyBeta("$_[0]\\source\\story.ni", "$betaDir\\source\\story.ni");

}

sub modifyBeta
{
  open(A, "$_[0]") || die ("Can't open source $_[0]");
  open(B, ">$_[1]") || die ("Can't open target $_[1]");

  my $foundBetaLine = 0;

  while ($a = <A>)
  {
    if ($a =~ /^volume beta testing/i) { print B "volume beta testing\n"; $foundBetaLine = 1; }
	elsif ($a =~ /\t\[showtime\]/)
	{
	my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time());
	print B sprintf("\tsay \"(Debug text, detailed time stamp in case I run 2 builds in a day) %d-%d-%d %d:%02d:%02d\"\n", $yearOffset + 1900, $month+1, $dayOfMonth, $hour, $minute, $second);
	}
	else { print B $a; }
  }
  close(A);
  close(B);
  if (!$foundBetaLine) { print "Warning: didn't find Beta line!"; }
}

sub i6exe
{
if (!$use6l{$_[0]})
{
  return "inform-633";
}
else
{
  return "inform6.exe";
}
}

sub buildDir
{
  if (!$use6l{$_[0]})
  {
    return "c:/program files (x86)/Inform 7";
  }
  my @altDir = ("c:/program files (x86)/Inform 76L", "d:/program files (x86)/Inform 7");
  for (0..$#altDir)
  {
    if (-d "$altDir[$_]")
    { return $altDir[$_]; }
  }
}

sub getFile
{
  open(A, "$_[0]") || die ("No blorb file $_[0]");

  while ($a = <A>)
  {
    if ($a =~ / leafname /) { chomp($a); $a =~ s/.* leafname \"//g; $a =~ s/\"//g; return $a; }
  }
  return "output.$ex";
}

sub delIfThere
{
  if (-f "$_[0]") { print "Deleting $_[0]\n"; system("erase \"$_[0]\""); } else { print "No $_[0]\n"; }
}

sub usage
{
print<<EOT;
USAGE
-ba = base dir specified default c:/games/inform/(project name).inform
-bd = base dir specified, default c:/games/inform/beta
-inf = create INF file only, no binary build
-jb -jd -jr just build/release/debug
-e edits the icl.txt file
EOT
exit
}