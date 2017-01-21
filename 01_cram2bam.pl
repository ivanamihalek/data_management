#!/usr/bin/perl
use strict;
use warnings;

@ARGV==1 || die "Usage: $0 <cramfile>. Bamfile will be written to the same directory.\n";
my $cramfile = $ARGV[0];

# the tools we need
my $samtools = "/usr/local/bin/samtools";
(-e $samtools) || die "$samtools not found.\n";

# the only case that I know how to resolve
# the header conaints @SQ linies with UR fields, all UR fields are the same, nad contain the path to
# a human assembly that I already have stored
my @lines = split "\n", `$samtools view -H $cramfile`;
for my $line (@lines) {
    $line =~  /\sUR\:(\S+)(\s|$)/|| next;
    my $assembly = pop(split "\/", $1);
    print $assembly , "\n";
}

# we have found the assembly, is it indexed?

# if not, index

