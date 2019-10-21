#####################################
#
# mytools.pm
#
# perl module
#
# general stuff that doesn't fall into Inform programming specifically
#

package mytools;

use Win32API::File qw( GetFileAttributes FILE_ATTRIBUTE_REPARSE_POINT );
use Win32::Symlink;

use strict;
use warnings;

use Exporter;

use vars qw($VERSION @ISA @EXPORT @EXPORT_OK %EXPORT_TAGS);

$VERSION     = 1.00;
@ISA         = qw(Exporter);
@EXPORT      = qw(follow_symlink);
#@EXPORT_OK   = qw(i7x $np);

sub follow_symlink
{
  my $temp = $_[0];
  my $last_temp = "";
  my $link_count = 0;

  return $_[0] if (! -f $_[0]);
  while (GetFileAttributes($temp) & FILE_ATTRIBUTE_REPARSE_POINT)
  {
    $last_temp = $temp;
    ( my $a2 = $temp ) =~ s/\//\\/g;
     my $q = `dir \"$a2\"`;
     $q =~ s/.*\[//sm;
     $q =~ s/].*//sm;
     $temp = $q;

    die("Recursive symlink $last_temp") if $last_temp eq $temp;
    $link_count += 1;
    die("Too many links") if $link_count > 10;
  }
  return $temp;
}

1;
