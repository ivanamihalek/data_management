#!/usr/bin/perl

@ARGV==1 || die "Usage: $0 <source_md5sum_file>\n";
my $source_md5sum_file = $ARGV[0];

@files  = split "\n", `ls`;

`touch md5sums`;

foreach my $file (@files)  { 
    $file eq $source_md5sum_file && next;
    print "$file\n";
    `md5sum $file >> md5sums`;
} 

print "md5sums difference: \n";
print `diff $source_md5sum_file  md5sums`;
print "********************* \n";
