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
my @assemblies;
for my $line (@lines) {
    $line =~  /\sUR\:(\S+)(\s|$)/|| next;
    my @aux = split "\/", $1;
    my $assembly = pop(@aux);
    my @foo = grep($assembly, @assemblies);
    next if @foo>0;
    @assemblies.push($assembly);
}

@assemblies==0 && die "no candidate assembly found in the header of $cramfile\n";
@assemblies>1 && die "I am not equipped to handle more than one assembly: @assemnlies\n";

my $reference_assembly = @assemblies[0];

print " reference assembly: $reference_assembly  \n";
# do we have the assembly at the expected location?

# we have found the assembly, is it indexed?

# if not, index

