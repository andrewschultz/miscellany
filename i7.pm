#####################################
#
#i7.pm
#
#perl module
#

package i7;

use strict;
use warnings;

use Exporter;

use vars qw($VERSION @ISA @EXPORT @EXPORT_OK %EXPORT_TAGS);

$VERSION     = 1.00;
@ISA         = qw(Exporter);
@EXPORT      = qw(%i7x);
#@EXPORT_OK   = qw(i7x);

our %i7x = ( "12" => "shuffling",
"sa" => "shuffling",
"roi" => "roiling",
"s13" => "roiling",
"3" => "threediopolis",
"13" => "threediopolis",
"14" => "ugly-oafs",
"oafs" => "ugly-oafs",
"s15" => "dirk",
"15" => "compound",
"4" => "fourdiopolis",
"s16" => "fourdiopolis",
"16" => "slicker-city",
"bs" => "btp-st",
"s17" => "btp-st"
);

1;
