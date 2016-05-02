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

$v6l = 0;

open(X, "c:/writing/scripts/icl.txt") || die ("Need icl.txt.");

while ($x = <X>)
{
  chomp($x);
  if ($x =~ /^;/) { last; }
  if ($x =~ /^#/) { next; }

  my @cmd = split(/=/, $x);
  if (lc(@cmd[0]) eq lc("default")) { @defaultCompileList = split(/,/, @cmd[1]); }
  elsif (lc(@cmd[0] eq lc "allproj")) { @allProj = split(/,/, $cmd[1]); }
  elsif ($x =~ /^z:/) { $y = $x; $y =~ s/^z://g; $zmac{$y} = 1; }
  elsif ($x =~ /^6l:/) { $y = $x; $y =~ s/^6l://g; $use6l{$y} = 1; }
  elsif ($#cmd > -1) { @froms = split(/,/, @cmd[0]); for (@froms) { $proj{$_} = $cmd[1]; } #print "$_ to $cmd[1].\n";
  }
}
#sensible abbreviations

#which projects are z machine? Default is glulx
$zmac{"compound"} = 0;
$zmac{"threediopolis"} = 1;
$zmac{"fourdiopolis"} = 0; #Needed to save states
$zmac{"dirk"} = 1;

$use6l{"compound"} = 0;

$runBeta = 0;
$debug = 0;
$release = 1;

$count = 0;

while ($count <= $#ARGV)
{

  $a = @ARGV[$count];
  for ($a)
  {
  #print "Argument " . ($a + 1) . " of " . ($#ARGV + 1) . ": $a\n";
  /^(b|beta)$/ && do { $runBeta = 1 - $runBeta; $count++; next; };
  /^-jb/ && do { $runBeta = 1; $debug = $release = 0; $count++; next; };
  /^-jd/ && do { $debug = 1; $runBeta = $release = 0; $count++; next; };
  /^-jr/ && do { $release = 1; $debug = $runBeta = 0; $count++; next; };
  /-f/ && do { $release = $debug = $beta = 0;
    if ($a =~ /r/) { $release = 1; }
    if ($a =~ /d/) { $debug = 1; }
    if ($a =~ /b/) { $runbeta = 1; }
	$count++; next;
  };
  /-l/ && do { $v6l = 1 - $v6l; $informDir = @inDirs[$v6l]; $count++; next; };
  /-nr/ && do { $release = 0; $count++; next; };
  /-yr/ && do { $release = 1; $count++; next; };
  /-nd/ && do { $debug = 0; $count++; next; };
  /-yd/ && do { $debug = 1; $count++; next; };
  /-x/ && do { $execute = 1; $count++; next; };
  /-a/ && do { for $entry(@allProj) { push(@compileList, $a); } $count++; next; };
  push(@compileList, $a); $count++; next;
  }
}

if ($#compileList == -1) { print "Nothing in compile list. Using default: @defaultCompileList.\n"; @compileList = @defaultCompileList; }

for $a (@compileList)
{
  if ($proj{$a}) { $myProj = $proj{$a}; }
  elsif ($proj{"-$a"}) { $myProj = $proj{"-$a"}; }
  else {
  $myProj = "";
  for $q (keys %proj) { if ($proj{$q} eq "$a") { $myProj = $a; } }
  if (!$myProj) { die("No project for $proj.\n"); }
  }
  $infDir = @inDirs[$v6l];
  runProj($myProj);
  $count++;
}

if (-f "gameinfo.dbg") { print "Deleting .dbg file\n"; unlink<gameinfo.dbg>; }

sub runProj
{
# this is bad coding but there's only two exceptions for now: Threediopolis and Dirk.
$ex = "ulx";
$gz = "gblorb";
$iflag = "G";
if ($zmac{$_[0]}) { $ex = "z8"; $gz = "zblorb"; $iflag = "v8"; }

$bdir = "c:\\games\\inform\\$_[0].inform";

$infDir = buildDir($_[0]);
$i6x = i6exe($_[0]);

if ($beta)
{
  #copyToBeta();
  $mat = "c:\\games\\inform\\$_[0].materials";
  $bmat = "c:\\games\\inform\\beta.materials";
  #if ($use6l{$_[0]}) { $mat =~ s/ materials/\.materials/g; $bmat =~ s/ materials/\.materials/g; }
  #doOneBuild("c:\\games\\inform\\beta.inform", "c:\\games\\inform\\beta Materials", "c:\\games\\inform\\$_[0].inform", "-kw~S~D$iflag");
}

if ($release)
{
  doOneBuild("$bdir", "~D", "c:\\games\\inform\\$_[0] Materials", "release");
}

if ($debug)
{
  #doOneBuild("$bdir", "D", "c:\\games\\inform\\$_[0] Materials", "debug");
}

}

sub doOneBuild
{
  $outFile = "$_[0]/Build/output.$ex";
  $dflag = "$_[1]";
  $infOut = "$_[0]/Build/auto.inf";
  
  delIfThere($infOut);
  system("\"$infDir/Compilers/ni\" -release -rules \"$infDir/Inform7/Extensions\" -package \"$_[0]\" -extension=$ex");

  if (! -f $infOut)
  {
    print "TEST RESULTS:$_[3] $_[0] i7->i6 failed,0,1,0\n";
    print "TEST RESULTS:$_[3] $_[0] i6->binary untested,grey,0,0\n";
    print "TEST RESULTS:$_[3] $_[0] blorb creation untested,grey,0,0\n";
	return;
  }

  delIfThere($outFile);
  system("\"$infDir/Compilers/$i6x\" -kw~S$dflag$iflag +include_path=$_[0] $infOut $outFile");
  
  if (! -f $outFile)
  {
    print "TEST RESULTS:$_[3] $_[0] i6->binary failed,0,1,0\n";
    print "TEST RESULTS:$_[3] $_[0] blorb creation untested,grey,0,0\n";
	return;
  }

  $blorbFileShort = getFile("$_[0]/Release.blurb");

  if ($_[3] eq "debug") { $blorbFileShort = "debug-$blorbFileShort"; }
  $outFinal = "$_[2]\\Release\\$blorbFileShort";
  delIfThere("$outFinal");
  sysprint("\"$infDir/Compilers/cblorb\" -windows \"$_[0]\\Release.blurb\" \"$outFinal\"");
  
  if ((! -f $outFinal) || (-s "\"$outFinal\"" < -s "\"$outFile\""))
  {
    print "TEST RESULTS:$_[3] $_[0] blorb creation failed,0,1,0\n";
	return;
  }

    print "TEST RESULTS:$_[3] $_[0] blorb creation passed,0,0,0\n";
  
  return;
}

sub sysprint
{
  print "$_[0]\n";
  system("$_[0]");
}

sub copyToBeta
{
print("set HOME=c:\\games\\inform\\beta.inform");
print "****BETA BUILD****\n";

system("copy $base\\Release.blurb $beta\\Release.blurb");
system("copy $base\\uuid.txt $beta\\uuid.txt");
print "Searching for cover....\n";

$cover = "$beta\\Cover";
$covr = "$beta\\Release\\Cover";
$smcov = "$beta\\Small Cover";
if (-f "$cover.jpg") { print "BETA: Erasing old jpg.\n"; system("Erase \"$cover.jpg\""); }
if (-f "$cover.png") { print "BETA: Erasing old png.\n"; system("Erase \"$cover.png\""); }
if (-f "$covr.png") { print "BETA: Erasing old Release\png.\n"; system("Erase \"$covr.png\""); }
if (-f "$covr.jpg") { print "BETA: Erasing old Release\jpg.\n"; system("Erase \"$covr.jpg\""); }
if (-f "$smcov.jpg") { print "BETA: Erasing old small jpg.\n"; system("Erase \"$smcov.jpg\""); }
if (-f "$smcov.png") { print "BETA: Erasing old small png.\n"; system("erase \"$smcov.png\""); }

if (-f "c:/games/inform/$_[0] materials/Cover.png") { print "Copying png over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Cover.png\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Cover.jpg") { print "Copying jpg over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Cover.jpg\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Small Cover.png") { print "Copying small png over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Small Cover.png\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Small Cover.jpg") { print "Copying small jpg over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Small Cover.jpg\" \"$bmat\""); }

modifyBeta("$base\\source\\story.ni", "$beta\\source\\story.ni");

}

sub modifyBeta
{
  open(A, "$_[0]") || die ("Can't open source $_[0]");
  open(B, ">$_[1]") || die ("Can't open target $_[1]");
  
  $foundBetaLine = 0;
  
  while ($a = <A>)
  {
    if ($a =~ /^volume beta testing/i) { print B "volume beta testing\n"; $foundBetaLine = 1; }
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
    if (-d "@altDir[$_]")
    { return @altDir[$_]; }
  }
}

sub getFile
{
  open(A, "$_[0]") || die ("No blorb file $_[0]");
  
  while ($a = <A>)
  {
    if ($a =~ / leafname /) { chomp($a); $a =~ s/.* leafname \"//g; $a =~ s/\"//g; return $a; }
  }
  return "output.$ext";
}

sub delIfThere
{
  if (-f "$_[0]") { print "Deleting $_[0]\n"; system("erase \"$_[0]\""); } else { print "No $_[0]\n"; }
}