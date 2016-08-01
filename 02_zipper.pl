#!/usr/bin/perl
use data_mgmt_utils_pl::md5 qw(get_md5sum);

$TEST_DRIVE = 0;

$fromdir = "/data01";

sub process_extension   (@_);

############### main ##################
#make_tarballs ("from_seq_center");
#exit;
# find all files that end in tar, fastq, bam and bzip2 them
process_extension("tar");
process_extension("fastq");
process_extension("gatk.vcf");


#######################################
sub process_extension (@_) {

    my $ext = $_[0];

    my @ext_files = `find $fromdir  -name "*.$ext"`;
    foreach $ext_file (@ext_files) {
        chomp $ext_file;
        print "$ext_file\n";
        (-e "$ext_file.bz2") && `rm $ext_file.bz2`;
        $cmd = "bzip2 $ext_file";
        if ($TEST_DRIVE) {
           print "$cmd\n";
        } else {
           (system $cmd) && die "error running $cmd\n";
           my ($md5sum, $dummy) = get_md5sum (0, $ext_file.".bz2");
           print "md5sum:   $md5sum\n";
        }
    }
}

#######################################
# the directory of "other" files from the sequencing center:
# make tarball and compress
sub make_tarballs (@_) {
    my $dirname = $_[0];
    my @dirs_to_compress = `find $fromdir  -name $dirname`;
    my $home = `pwd`; chomp $home;
    foreach my $dir (@dirs_to_compress) {
        chomp $dir;
        my @aux = split '/', $dir;
        my $dirname = pop @aux; # should be "from_seq_center" in this case
        my $path = join '/', @aux;
        print "\n$path\n";
        chdir $path;
        foreach my $cmd  ("tar -cf $dirname.tar $dirname", "rm -r $dirname") {
            if ($TEST_DRIVE) {
               print "$cmd\n";
            } else {
                print "$cmd  \n";
               (system $cmd) && die "error running $cmd\n";
               #exit(1)
            }
        }
        chdir $home;
    }
}