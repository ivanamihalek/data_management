package md5;
use strict;
use warnings;

#########################################################
sub get_md5sum (@_) {
    my $check_old_md5 = $_[0];
    my $ext_file = $_[1];
    my @aux = split '/', $ext_file;
    my $filename = pop @aux;
    my $dirpath = join "/", @aux;
    $dirpath .= "/md5sums";
    ( -d $dirpath) || `mkdir $dirpath`;
    my $md5sum_file = "$dirpath/$filename.md5";
    ($check_old_md5 && -e $md5sum_file && ! -z $md5sum_file) || `md5sum $ext_file | cut -d' ' -f 1 > $md5sum_file`;
    push @resolved_files, $md5sum_file; #this is our md5sum, we will not copy it as "other files from seq center"

    my $md5  = "" || `cat $md5sum_file  | cut -d' ' -f 1`; chomp $md5;
    $md5 ne "" or die "error obtaining $md5sum_file\n";
    return $md5;
}

