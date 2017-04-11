#!/usr/bin/perl

# this is a hack, written originally in attempt to sort through the mess
# of semi-organized legacy data
# it expects to be given a directory path, in which the case (family) subdirs can be found
# the names of the individual files should contain the individual (family member id)
# after that, the script attempts to guess the file type and sort it accordingly
# in the local archive
use warnings;
use strict;

use data_mgmt_utils_pl::md5 qw(get_md5sum);

my $TEST_DRIVE = 1;  # test drive will only create the target directory structure

# space handling in the path names does not work well and I have to move on, hence the 00_clean.pl

#@ARGV==1 || die "Usage: $0 <fromdir>\n";
my $fromdir = "/mnt/usb";
my @cases  = ('BO16046', 'BO16049', 'BO17006');

-e $fromdir || die "$fromdir not found.\n";
-d $fromdir || die "$fromdir does not seem to be a directory.\n";

my %ext2dirname = ("vcf"=> "variants/called_by_seq_center", "bam"=>"alignments/by_seq_center",
    "bai"=> "alignments/by_seq_center", "fastq" => "reads", "txt" => "reads");

#my %ext2dirname = ("vcf"=> "variants/called_by_seqmule_pipeline", "bam"=>"alignments/by_seqmule_pipeline",
#		   "bai"=> "alignments/by_seqmule_pipeline", "fastq" => "reads", "txt" => "reads");


####################################################


sub parse_case_id (@);
sub process_extension   (@);
sub check_for_leftovers (@);

my %seen = ();

my @resolved_files = ();
my %resolved  = ();


####################################################
for my $case_id (@cases) {

    print "\n$case_id\n";
    my ($bo, $year, $caseno) = parse_case_id($case_id);
    my $case_boid = $bo.$year.$caseno ;
    print " $year   $caseno   $case_boid  \n";
    length $case_boid == 7 || die "bad BOID:  $case_boid   ($year $caseno) \n";
    continue;
#    my $todir  = "/data01";
#    if ($year eq "16" or  $year eq "17") {$todir  = "/data02";}
#    -e $todir || die "$todir not found.\n";
#
#    my $casedir = "$todir/20$year/$caseno";
#
#    if (defined $seen{$casedir}) {
#        die "$casedir seen twice\n";
#    } else {
#        $seen{$casedir} = 1;
#    }
#    (-e $casedir) || `mkdir -p $casedir`;
#
#    (defined $project) && `echo $project > $casedir/PROJECT`;
#
#
#    process_extension($fromdir, $case,  $year, $caseno, $casedir, "txt");
#    process_extension($fromdir, $case,  $year, $caseno, $casedir, "vcf");
#    process_extension($fromdir, $case,  $year, $caseno, $casedir, "bam");
#    process_extension($fromdir, $case,  $year, $caseno, $casedir, "bai");
#    process_extension($fromdir, $case,  $year, $caseno, $casedir, "fastq");
#
#    # turn to indicator hash:
#    %resolved = map { $_ =>  1 } @resolved_files;
#    check_for_leftovers ("$fromdir/$case", "$casedir/other/from_seq_center");
}

$TEST_DRIVE && printf "\n please check for BAM, FASTQ and VCF (uppercase) extensions\n\n";


##################################################################################################
sub parse_case_id (@_){
    my $case_id = $_[0];
    my ($bo, $year, $caseno) = ();
    my $len = length($case_id);

    # old case id format
    if ($case_id =~ "-" ) {
        ($bo, $year, $caseno) = split "-", $case_id;
        (length($year)==4)  && ($year = substr $year, 2,2);
        (length($caseno) ==2)  || die  "Unexpected BOid format: $case_id\n";

    } elsif ($len==6) { # the new BOid format
        $bo         = substr $case_id, 0, 2;
        $year       = substr $case_id, 2, 2;
        $caseno     = substr $case_id, 4, 2;

    } elsif ($len==7) { # the new new BOid format
        $bo         = substr $case_id, 0, 2;
        $year       = substr $case_id, 2, 2;
        $caseno     = substr $case_id, 4, 3;

    } else {
        die  "Unexpected BOid format: $case_id\n";
    }

    if (length ($caseno) == 3) {

    }  elsif (length ($caseno) == 2) {
        $caseno = "0".$caseno;
    }  else {
        die  "Unexpected BOid format: $case_id (case number $caseno ?)\n";
    }

    return ($bo, $year, $caseno) ;
}


##################################################################################################
sub check_for_leftovers (@_) {

    my ($thing, $target_dir) = @_;
    my $thing_no_space = $thing;
    $thing_no_space =~ s/([\s\(\)])/\\$1/g;

    if (-f $thing) {

        if (not defined $resolved{$thing_no_space} ) {

            my @path = split "/", $target_dir;
            my $name = pop @path;
            $name =~ s/([\(\)])/\\$1/g;
            my $path = join "/", @path;
            $path =~ s/ /_/g;
            $path =~ s/([\(\)])/\\$1/g;
            (-e $path) || `mkdir -p $path`;
            if ($TEST_DRIVE) {
                `touch $path/$name`;
            } else {
                `cp $thing_no_space $path/$name`;
            }
        }

    } elsif (-d $thing) {
        my @subs = split "\n", `ls $thing_no_space`;
        foreach my $subdir (@subs) {
            check_for_leftovers ("$thing/$subdir", "$target_dir/$subdir");
        }
    }

    return;
}


##################################################################################################
sub process_extension (@_) {

    printf "processing extension @_ \n";
    my ($fromdir, $case, $year, $caseno, $casedir, $ext) = @_;

    my @ext_files = `find $fromdir/$case  -name "*.$ext*"`;

    my $incomplete = 0;
    foreach my $ext_file (@ext_files) {
        next if $ext_file =~ /\.md5$/;
        chomp $ext_file;
        my ($year2, $caseno2, $individual2);

        if ( $ext_file =~ /.*BO\-(\d{4}\-\d{2}\-I+\w{1})(_*.*\.$ext.*)/ ) {
            #defined $1 or die "boid could not be extracted:\n$ext_file\n";
            if ( ! defined $1) {
                #print "boid could not be extracted:\n$ext_file\n";
                next;
            }
            ($year2, $caseno2, $individual2) = split "-", $1;
            $year2 = substr $year2, 2, 2;
            if ($individual2 =~ /III/) {
                $individual2 =~ s/III/3/;

            } elsif ($individual2 =~ /II/) {
                $individual2 =~ s/II/2/;

            }  elsif ($individual2 =~ /I/) {
                $individual2 =~ s/I/1/;
            }


        } elsif  ( $ext_file =~ /.*BO(\d{5}[ABCDE]{1})(_*.*\.$ext.*)/ ) {
            $year2 = substr $1, 0, 2;
            $caseno2 = substr $1, 2, 2;
            $individual2 = substr $1, 4, 2;

        } elsif  ( $ext_file =~ /.*BO(\d{6}[ABCDE]{1})(_*.*\.$ext.*)/ ) {
            $year2 = substr $1, 0, 2;
            if ($caseno ==  substr $1, 2, 3)  {
                $caseno2 = substr $1, 2, 3;
            } else {
                $caseno2 = substr $1, 2, 2; # Christina is adding in an extra 0 on the right
            }
            $individual2 = substr $1, 5, 2;
        }

        while ( length($caseno2)<3 ) {
            $caseno2 = "0". $caseno2;
        }
        ($year== $year2 &&   $caseno==$caseno2) ||
            die ">> label mismatch for $case:\n$ext_file\n yr:$year  yr2:$year2  caseno:$caseno  caseno2:$caseno2 \n";

        my $boid = "BO".$year.$caseno.$individual2;

        my $orig_file = $2;
        $ext_file =~ s/([\s\(\)])/\\$1/g; # I do not want quotemeta here bcs slashes are meaningful
        $incomplete = ($ext_file =~  /incomplete/ );

        # special for txt files that are actually fastq (...)
        if ( $ext eq "txt") {
            my $is_fastq = 0;

            # it would take too long to unzip all fastq files, so I'll take the shortcut
            # 1) the file with extension txt is fastq if it is in the fastq directory
            # 2) the file with extension txt is fastq if it starts with @
            # 3) only if the above two fail, go and unzip
            if ($ext_file =~ /fastq/i || $ext_file =~ /sequence/) {
                my $size  = `ls -l $ext_file | cut -d' ' -f 5`; chomp $size;
                $size /= 1024*1024;  $size = int $size;
                $size > 0 and ($is_fastq = 1);

            } elsif ($ext_file =~ /gz$/ || $ext_file =~ /bz2$/ || $ext_file =~ /zip$/) {
                printf "need to unpack $ext_file\n";
                exit;
            } else {
                my @lines = split "\n", `head -n 12 $ext_file`;

                foreach  my $line_ct (0 .. 9) {
                    $lines[$line_ct] =~ /^\@/ && $lines[$line_ct+2] =~ /^\+/ || next;
                    $is_fastq = 1;
                    last;
                }
            }
            $is_fastq || next;
        }

        my $boiddir = "$casedir/$boid";
        (-e $boiddir) || `mkdir $boiddir`;

        my $extdir = "$boiddir/wes/$ext2dirname{$ext}";
        (-e $extdir) || `mkdir -p  $extdir`;

        $incomplete && `echo some $ext files might be incomplete >> $extdir/NOTES`;

        my $new_extension = $orig_file;


        if ($ext eq  "txt") {
            $new_extension =~ s/(.*)txt/$1fastq/;
        }

        my $newfile = "$extdir/$boid"."$new_extension";

        if ($TEST_DRIVE) {
            `touch $newfile`;

        } else {

            my $need_to_copy = 1;
            my $check_old_md5 = 1;
            if ( -e  $newfile && ! -z $newfile) {
                print "\t $newfile found\n";
                $check_old_md5 = 1;
                # have we calculated the md5 sum already?
                # always check for the old md5 in the "from" directory
                my ($md5orig, $md5sum_file) = get_md5sum (1, $ext_file);
                push @resolved_files, $md5sum_file; #this is our md5sum, we will not copy it as "other files from seq center"
                my  ($md5new, $dummy) = get_md5sum ($check_old_md5, $newfile);
                print "\t $md5orig\n";
                print "\t $md5new\n";
                $md5orig == $md5new && ($need_to_copy = 0);
            }
            if ($need_to_copy) {
                print "\t copying to $newfile \n";
                $check_old_md5 = 0; # in case we have a leftover
                `cp $ext_file $newfile`;
                my ($md5orig, $md5sum_file) = get_md5sum (1, $ext_file);
                push @resolved_files, $md5sum_file; #this is our md5sum, we will not copy it as "other files from seq center"
                my ($md5new, $dummy) = get_md5sum ($check_old_md5, $newfile);
                print "\t $md5orig\n";
                print "\t $md5new\n";
                $md5orig == $md5new || die "md5 sum mismatch\n";
            }
        }
        push @resolved_files, $ext_file;
    }
}
