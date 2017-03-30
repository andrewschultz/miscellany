##############################
#
#ses.pl
#
#calculates the number of open and new files in Notepad++
#
#no cmd line arguments besides e and ?

use strict;
use warnings;

my $totalFiles=0;
my $newFiles=0;

my $npSes = "C:\\Users\\Andrew\\AppData\\Roaming\\Notepad++\\session.xml";

open(A, $npSes) || die ("Can't open $npSes");

while ($a = <A>)
{
  if ($a =~ /^[ \t]*<File /)
  {
    $totalFiles++;
    if ($a =~ /\"new [0-9]+\"/)
    { $newFiles++; }
  }

}

print "TEST RESULTS:Notepad++ tabs,25,$totalFiles,0,(none yet)\n";
print "TEST RESULTS:Notepad++ new files,15,$newFiles,0,(none yet)\n";
