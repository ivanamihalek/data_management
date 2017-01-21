#!/usr/bin/perl

use strict;
use warnings;

# prerequisites
my $samtools = "/usr/local/bin/samtools";
for ($samtools) {
    -e $_ || die "$_ not found.\n";
}
die "$0 not implemented ...\n";
# samtools merge merged.bam in.1.bam in.2.bam ...
