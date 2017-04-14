#!/usr/bin/perl

use strict;
use warnings;
@ARGV==2|| die "Usage: $0  <target dir>  <source_md5sum_file>\n";
my $target_dir         = $ARGV[0];
my $source_md5sum_file = $ARGV[1]; # format: <md5sum> <filepath>

my @md5_files  = split "\n", `find $target_dir -name '*md5'`;

foreach my $md5_file_path (@md5_files)  {
    my @aux = split "/", $md5_file_path;
    my $md5_file = pop @aux;
    my $file = $md5_file; $file =~ s/\.md5$//;
    print "\n";
    print "$file\n";
    my $ret =  `grep $file $source_md5sum_file`;
    @aux = split /\s+/, $ret;
    my $source_md5 = $aux[0];
    my $target_md5 = `cat $md5_file_path`; chomp $target_md5;
    print "src: $source_md5\ntgt: $target_md5\n";
    $source_md5 eq $target_md5 || die "md5 mismatch.\n";
}
