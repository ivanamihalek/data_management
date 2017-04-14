#!/usr/bin/perl

use strict;
use warnings;
@ARGV==2|| die "Usage: $0  <target dir>  <source_md5sum_file>\n";
my $target_dir         = $ARGV[0];
my $source_md5sum_file = $ARGV[1];

my @md5_files  = split "\n", `find $target_dir -name '*md5'`;

foreach my $md5_file_path (@md5_files)  {
    my @aux = split "/", $md5_file_path;
    my $md5_file = pop @aux;
    print "$md5_file\n";

}

exit;

=pod
`touch md5sums`;

foreach my $file (@files)  { 
    $file eq $source_md5sum_file && next;
    print "$file\n";
    `md5sum $file >> md5sums`;
} 

print "md5sums difference: \n";
print `diff $source_md5sum_file  md5sums`;
print "********************* \n";
=cut