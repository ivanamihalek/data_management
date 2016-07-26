 #!/usr/bin/perl

 $ext_file = "/mnt/bodamer02/BO-2012-03_MR/fastq\ Files/BO-2012-03-IA_MR_201306686-05_S_6_1.txt.bz2";
  my @aux = split '\/', $ext_file;
  print join "     ", @aux;
  print "\n";

    my $filename = pop @aux;
    print "$filename\n";
    my $dirpath = join "/", @aux;
    $dirpath .= "/md5sums";
    print $dirpath, "\n";


    #(-e $dirpath) || `mkdir $dirpath`;
    my $md5sum_file = "$dirpath/$filename.md5";

    print "$ext_file\n";
    print "$md5sum_file\n";
