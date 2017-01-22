#!/usr/bin/perl
# note: cram - bam - cram does not recover the original file because samtools change the header

use strict;
use warnings;

@ARGV==1 || die "Usage: $0 <cramfile>. Bamfile will be written to the same directory.\n";
my $cramfile = $ARGV[0];

# prerequisites
my $samtools = "/usr/local/bin/samtools";
my $ref_assembly_dir = "/databases/human_genome";
for ($samtools, $ref_assembly_dir) {
    -e $_ || die "$_ not found.\n";
}

# the only case that I know how to resolve
# the header conaints @SQ lines with UR fields, all UR fields are the same, and contain the path to
# a human assembly that I already have stored
my @lines = split "\n", `$samtools view -H $cramfile`;
my @assemblies;
for my $line (@lines) {
    $line =~  /\sUR\:(\S+)(\s|$)/|| next;
    my @aux = split "\/", $1;
    my $assembly = pop(@aux);
    my @foo = grep($assembly, @assemblies);
    next if @foo>0;
    push @assemblies, $assembly;
}

@assemblies==0 && die "no candidate assembly found in the header of $cramfile\n";
@assemblies>1 && die "I am not equipped to handle more than one assembly: @assemblies\n";

my $reference_assembly = $assemblies[0];

print " reference assembly: $reference_assembly  \n";
# do we have the assembly at the expected location?
my $ref_fullpath = join("/",$ref_assembly_dir, $reference_assembly);
(-e $ref_fullpath) || die "$reference_assembly not found in $ref_assembly_dir\n";
(-z $ref_fullpath) && die "$ref_fullpath is empty\n";

# we have found the assembly, is it indexed?  if not, index
my $ref_assembly_index = $ref_fullpath.".fai";
(-e $ref_assembly_index  && ! -z $ref_assembly_index )  || `$samtools faidx $ref_fullpath`;
(-e $ref_assembly_index  && ! -z $ref_assembly_index )  || die "failed to index $ref_fullpath\n";

# finally, make the cramfile
my $bamfile = $cramfile;
$bamfile =~ s/cram$/bam/;
$bamfile ne $cramfile || die "failed to create bamfile name (does cramfile have the extenion \"cram\"?)\n";
my $cmd = "$samtools view $cramfile -T $ref_fullpath -b -o $bamfile";
print "running $cmd \n";
(system $cmd) && die "Error running $cmd: $!\n";


