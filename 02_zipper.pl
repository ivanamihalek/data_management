#!/usr/bin/perl

$TEST_DRIVE = 0;

$fromdir = "/data02";

sub process_extension   (@_);

############### main ##################
make_tarballs ("from_seq_center");
exit;
# find all files that end in tar, fastq, bam and bzip2 them
process_extension("tar");
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
    my $home = `pwd`; chomp $home;
    foreach my $dir (@dirs_to_compress) {
        chomp $dir;
        chdir $home;
        my @aux = split '/', $dir;
        my $dirname = pop @aux; # should be "from_seq_center" in this case
        my $path = join '/', @aux;
        print "$path\n";
        chdir $path;
        #foreach my $cmd  ("tar -cf $dir.tar $dir", "bzip2 $dir.tar", "rm -r $dir") {
        foreach my $cmd  ("tar -cf $dirname.tar $dirname") {
            if ($TEST_DRIVE) {
               print "$cmd\n";
            } else {
                print "$cmd  \n";
               (system $cmd) && die "error running $cmd\n";
               #exit(1)
            }
        }
        exit;
    }
}