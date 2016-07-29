#!/usr/bin/perl

$TEST_DRIVE = 0;

$fromdir = "/data02";

sub process_extension   (@_);

############### main ##################
make_tarballs ("from_seq_center");
# find all files that end in tar, fastq, bam and bzip2 them
process_extension("bam");
process_extension("fastq");


#######################################
# recalculate the md5sum
sub process_extension (@_) {

    my $ext = $_[0];

    my @ext_files = `find $fromdir  -name "*.$ext"`;
    foreach $ext_file (@ext_files) {
        chomp $ext_file;
        print "$ext_file\n";
        $cmd = "bzip2 $ext_file";
        if ($TEST_DRIVE) {
           print "$cmd\n";
        } else {
           #system $cmd && die "error running $cmd\n";
           #exit(1)
        }
    }
}

# the directory of "other" files from the sequencing center:
# make tarball and compress
sub make_tarballs (@_) {
    my $dirname = $_[0];
    my @dirs_to_compress = `find $fromdir  -name $dirname`;
    foreach my $dir (@dirs_to_compress) {
        chomp $dir;
        print "$dir\n";
        #foreach my $cmd  ("tar -cf $dir.tar $dir", "bzip2 $dir.tar", "rm -r $dir") {
        foreach my $cmd  ("tar -cf $dir.tar $dir", "bzip2 $dir.tar") {
            if ($TEST_DRIVE) {
               print "$cmd\n";
            } else {
               system $cmd && die "error running $cmd\n";
               #exit(1)
            }
        }
        exit;
    }
}