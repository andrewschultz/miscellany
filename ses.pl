##############################
#
#ses.pl
#
#calculates the number of open and new files in Notepad++
#
#no cmd line arguments besides e and ?

use strict;
use warnings;

my %sizes;

my $totalFiles=0;
my $newFiles=0;

my $npSes = "C:\\Users\\Andrew\\AppData\\Roaming\\Notepad++\\session.xml";

if (defined($ARGV[0]) && ($ARGV[0] =~ /^-?e$/))
{
  `$npSes`;
  exit();
}

open(A, $npSes) || die ("Can't open $npSes");

while ($a = <A>)
{
  chomp($a);
  if ($a !~ /backupfilepath/i) { next; }
  my @b = split(/\"/, $a);
  my $fileName = $b[17];
  my $fileBackup = $b[19];
  if ($a =~ /^[ \t]*<File /)
  {
    $totalFiles++;
    if ($a =~ /\"new [0-9]+\"/)
    { $newFiles++; }
	if ($fileName =~ /^new [0-9]/)
	{
	  $sizes{$fileName} = -s "$fileBackup";
	}
  }

}


my $news;
my $count = 0;

for my $x (sort {$sizes{$a} <=> $sizes{$b}} keys %sizes)
{
  $news .= "$x ($sizes{$x})<br />";
  $count++; if ($count == 5) { last; }
}

print "TEST RESULTS:Notepad++ tabs,25,$totalFiles,0,(none yet)\n";
print "TEST RESULTS:Notepad++ new files,15,$newFiles,0,$news\n";
