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

$infDir = buildDir($_[0]);
$i6x = i6exe($_[0]);

$beta = "c:\\games\\inform\\beta.inform";
$betm = "c:\\games\\inform\\beta Materials";
$base = "c:\\games\\inform\\$_[0].inform";

if ($use6l{$_[0]})
{
$mat = "c:\\games\\inform\\$_[0].materials";
$bmat = "c:\\games\\inform\\beta.materials";
}
else
{
$mat = "c:\\games\\inform\\$_[0] materials";
$bmat = "c:\\games\\inform\\beta materials";
}

$bdir = "$base\\Build";

#die ("$runBeta $debug $release");
`cd c:/games/inform/$_[0].inform/Build`;
if ($runBeta)
{

print("set HOME=c:\\games\\inform\\beta.inform");
print "****BETA BUILD****\n";

system("copy $base\\Release.blurb $beta\\Release.blurb");
system("copy $base\\uuid.txt $beta\\uuid.txt");
print "Searching for cover....\n";

$cover = "$beta\\Cover";
$covr = "$beta\\Release\\Cover";
$smcov = "$beta\\Small Cover";
if (-f "$cover.jpg") { print "Erasing old jpg.\n"; system("erase \"$cover.jpg\""); }
if (-f "$cover.png") { print "Erasing old png.\n"; system("erase \"$cover.png\""); }
if (-f "$covr.png") { print "Erasing old Release\png.\n"; system("erase \"$covr.png\""); }
if (-f "$covr.jpg") { print "Erasing old Release\jpg.\n"; system("erase \"$covr.jpg\""); }
if (-f "$smcov.jpg") { print "Erasing old small jpg.\n"; system("erase \"$smcov.jpg\""); }
if (-f "$smcov.png") { print "Erasing old small png.\n"; system("erase \"$smcov.png\""); }

if (-f "c:/games/inform/$_[0] materials/Cover.png") { print "Copying png over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Cover.png\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Cover.jpg") { print "Copying jpg over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Cover.jpg\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Small Cover.png") { print "Copying small png over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Small Cover.png\" \"$bmat\""); }
if (-f "c:/games/inform/$_[0] materials/Small Cover.jpg") { print "Copying small jpg over.\n"; system("copy \"c:\\games\\inform\\$_[0] materials\\Small Cover.jpg\" \"$bmat\""); }

modifyBeta("$base\\source\\story.ni", "$beta\\source\\story.ni");

$outFile = "$beta/Build/output.$ex";
delIfThere($outFile);

system("\"$infDir/Compilers/ni\" -release -rules \"$infDir/Inform7/Extensions\" -package \"$beta\" -extension=$ex");
system("\"$infDir/Compilers/$i6x\" -kw~S~D$iflag +include_path=$beta,$beta $beta/Build/auto.inf $beta/Build/output.$ex");

$betaFileShort = getFile("$beta/Release.blurb");

if (! -f $outFile) { print ("TEST RESULTS:$_[0] BETA,0,0,0,$outFile built\n"); print ("TEST RESULTS:$_[0] BETA BLORB,-1,0,0,Blorb build not attempted\n"); }
else
{
$outFile = "$betm/Release/beta-$betaFileShort";

delIfThere($outFile);
print("\"$infDir/Compilers/cblorb\" -windows $beta/Release.blurb $outFile");
system("\"$infDir/Compilers/cblorb\" -windows \"$beta/Release.blurb\" \"$outFile\"");
if (-f "$outFile") { print ("TEST RESULTS:$_[0] BETA,0,0,0,$outFile built\n"); }
else { print ("TEST RESULTS:$_[0] BETA,0,1,0,$outFile failed\n"); }
if ($execute) { $execute = 0; `$beta/Release.blurb $beta/Build/output.$gz`; }
}

}
if ($debug)
{
system("set HOME=c:\\games\\inform\\beta.inform");
printf "Debug build.\n";

$outFile = "$bdir/output.$ex";
delIfThere($outFile);
system("\"$infDir/Compilers/ni\" -rules \"$infDir/Inform7/Extensions\" -package \"$base\" -extension=$ex");
system("\"$infDir/Compilers/$i6x\" -kwSD$iflag +include_path=$base,$bdir $bdir/auto.inf \"$bdir/output.$ex\"");
if (-f "$outFile") { print ("TEST RESULTS:$_[0] DEBUG,0,0,0,$outFile built\n"); }
else { print ("TEST RESULTS:$_[0] DEBUG,0,1,0,$outFile failed\n"); }
if ($execute) { $execute = 0; `$bdir/output.$ex`; }
}
if ($release)
{
system("cd $base");
printf "Release build.\n";

$outFile = "$bdir\\output.$ex";
delIfThere($outFile);

printf "Generating output.$ex.\n";
#die("\"$infDir/Compilers/ni\" -release -rules \"$infDir/Inform7/Extensions\" -package \"$base\" -extension=$ex");
system("\"$infDir/Compilers/ni\" -release -rules \"$infDir/Inform7/Extensions\" -package \"$base\" -extension=$ex");
printf "Generating blorb.$ex.\n";
$outFile = "$bdir/output.$ex";
delIfThere($outFile);
system("\"$infDir/Compilers/$i6x\" -kw~S~D$iflag +include_path=$base,$bdir $bdir/auto.inf \"$outFile\"");
if (-f "$outFile") { print ("TEST RESULTS:$_[0] RELEASE,0,0,0,$outFile built\n");
#the below doesn't work as in the Windows compiler, so we have to explicitly set paths
#system("\"C:/Program Files (x86)/Inform 7/Compilers/cblorb\" -windows Release.blurb Build/output.gblorb");
printf "Bundling for release.\n";
$outFile = "$bdir/output.$gz";
system("\"$infDir/Compilers/cblorb\" -windows $base/Release.blurb $bdir/output.$gz");
if (-f "$outFile") { print ("TEST RESULTS:$_[0] BLORB RELEASE,0,0,0,$outFile built\n"); }
else { print ("TEST RESULTS:$_[0] BLORB RELEASE,0,1,0,$outFile failed\n"); }
$fileShort = getFile("$base/Release.blurb");
$rdir = "$base\\Release";
$rdir =~ s/\.inform/ Materials/g;
$cpString = "copy $bdir\\output.$gz \"$rdir\\$fileShort\""; `$cpString`;
if ($execute) { $execute = 0; `$bdir/output.$gz`; }
}
else
{
  print ("TEST RESULTS:$_[0] RELEASE,0,1,0,$outFile failed\n");
  print ("TEST RESULTS:$_[0] BLORB RELEASE,0,-1,0,$outFile failed\n");
}
}
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
for (0..$#altDir) { if (-d "@altDir[$_]") { return @altDir[$_]; } }
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
  if (-f "$_[0]") { system("erase \"$_[0]\""); }
}