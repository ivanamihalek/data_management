#!/usr/bin/perl
use data_mgmt_utils_pl::md5;


# space handling in the path names does not work well and I have to move on, hence the 00_clean.pl

@ARGV==1 || die "Usage: $0 <fromdir>\n";
my $fromdir = $ARGV[0];


%ext2dirname = ("vcf"=> "variants/called_by_seq_center", "bam"=>"alignments/by_seq_center", "bai"=>"alignments/by_seq_center",
		 "fastq" => "reads", "txt" => "reads");


if ($fromdir eq  "/mnt/bodamer02") {
    $todir = "/data01";
} elsif ($fromdir eq  "/mnt/bodamer01"){
    $todir = "/data02";
} else {
    die "Unexpected fromdir: $fromdir\n";
}


-e $fromdir || die "$fromdir not found.\n";
-d $fromdir || die "$fromdir does not seem to be a directory.\n";

-e $todir || `mkdir $todir`;
-d $fromdir || die "$todir does not seem to be a directory.\n";


sub process_extension   (@_);
sub check_for_leftovers (@_);
sub get_md5sum (@_);

$TEST_DRIVE = 0;

@listing_level_1 = split "\n", `ls $fromdir`;

@cases  = ();
 
foreach ( @listing_level_1 ) {
    if( -d "$fromdir/$_") {
       /^BO/  && push @cases, $_;
    }
}


%seen = {};


for $case (@cases) {
    
    print "\n$case\n";
    @listing_level_2 = split "\n", `ls $fromdir/$case`;

    @dirs = ();
    @files = ();
    foreach ( @listing_level_2 ) {
	if( -d "$fromdir/$case/$_") {
	    push @dirs, $_;
	    #print "\t  dir: $_\n";
	} else {
	    push @files, $_;
	    #print "\t file: $_\n";
	}
    }
    ($case_id, $project) = split "_", $case;
    undef $individual;
    ($bo, $year, $caseno, $individual) = split "-", $case_id;

    (length($caseno) ==2)  || die  "Unexpected BOid format: $case_id\n";
    $caseno = "0".$caseno;

    $case_boid = $bo.$year.$caseno;
    length $case_boid == 9 || die "bad BOID:  $bo   $year $caseno \n";
    print " $year   $caseno   $case_boid    $project \n";

    $project =~ s/201402006.ACE/FilaminC/g;
    $project =~ s/\-GeneDx//g;

    $casedir = "$todir/$year/$caseno";
    
    if (defined $seen{$casedir}) {
	    die "$casedir seen twice\n";
    } else {
	    $seen{$casedir} = 1;
    }
    (-e $casedir) || `mkdir -p $casedir`;

    `echo $project > $casedir/PROJECT`;

    @resolved_files = ();

    process_extension("txt");
    process_extension("vcf");
    process_extension("bam");
    process_extension("bai");
    process_extension("fastq");

    # turn to indicator hash:
    %resolved = map { $_ =>  1 } @resolved_files;
    check_for_leftovers ("$fromdir/$case", "$casedir/other/from_seq_center");
}

$TEST_DRIVE && printf "\n please check for BAM, FASTQ and VCF (uppercase) extensions\n\n";



##################################################################################################
sub check_for_leftovers (@_) {

    my ($thing, $target_dir) = @_;
    my $thing_no_space = $thing;
    $thing_no_space =~ s/([\s\(\)])/\\$1/g;

    if (-f $thing) {

        if (not defined $resolved{$thing_no_space} ) {

            @path = split "/", $target_dir;
            my $name = pop @path;
            $name =~ s/([\(\)])/\\$1/g;
            $path = join "/", @path;
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

    my $ext = $_[0];
    
    my @ext_files = `find $fromdir/$case  -name "*.$ext*"`;

    $incomplete = 0;
    foreach $ext_file (@ext_files) {
        next if $ext_file =~ /\.md5$/;
        chomp $ext_file;
        $ext_file =~ /.*BO\-(\d{4}\-\d{2}\-I+\w{1})_(.*\.$ext.*)/;
        #defined $1 or die "boid could not be extracted:\n$ext_file\n";
        if ( ! defined $1) {
            #print "boid could not be extracted:\n$ext_file\n";
            next;
        }
        ($year2, $caseno2, $individual2) = split "-", $1;
        (length($caseno2)==2)  || die  "Unexpected BOid format: $1\n";
        $caseno2 = "0".$caseno2;
        $orig_file = $2;
        $ext_file =~ s/([\s\(\)])/\\$1/g; # I do not want quotemeta here bcs slashes are meaningful
        $incomplete = ($ext_file =~  /incomplete/ );


        # special for txt files that are actually fastq (...)

        if ( $ext eq "txt") {
            my $is_fastq = 0;

            # it would take too long to unzip all fastq files, so I'll take the shorrtcut
            # 1) the file with extenxion txt is fastq if it is in the fastq directory
            # 2) the file with extenxion txt is fastq if it starts with @
            # 3) only if the above two fail, go and unzip
            if ($ext_file =~ /fastq/i || $ext_file =~ /sequence/) {
                $size  = `ls -l $ext_file | cut -d' ' -f 5`; chomp $size;
                $size /= 1024*1024;  $size = int $size;
                $size > 0 and ($is_fastq = 1);

            } elsif ($ext_file =~ /gz$/ || $ext_file =~ /bz2$/ || $ext_file =~ /zip$/) {
                printf "need to unpack $ext_file\n";
                exit;
            } else {
                @lines = split "\n", `head -n 12 $ext_file`;

                foreach $line_ct (0 .. 9) {
                    $lines[$line_ct] =~ /^\@/ && $lines[$line_ct+2] =~ /^\+/ || next;
                    $is_fastq = 1;
                    last;
                }
            }
            $is_fastq || next;
        }
	
        ($year== $year2 &&   $caseno==$caseno2) || die ">> label mismatch for $case:\n$ext_file\n $year  $year2  $caseno  $caseno2 \n";
        (defined $individual &&  $individual ne $individual2)  && die "** label mismatch for $case:\n$ext_file\n";

        if ($individual2 =~ /III/) {
            $individual2 =~ s/III/3/;

        } elsif ($individual2 =~ /II/) {
            $individual2 =~ s/II/2/;

        }  elsif ($individual2 =~ /I/) {
            $individual2 =~ s/I/1/;
        }

        $boid = $bo.(substr $year, 2, 2).$caseno.$individual2;


        $boiddir = "$casedir/$boid";
        (-e $boiddir) || `mkdir $boiddir`;

        $extdir = "$boiddir/wes/$ext2dirname{$ext}";
        (-e $extdir) || `mkdir -p  $extdir`;

        $incomplete && `echo some $ext files might be incomplete >> $extdir/NOTES`;

        $new_name = $orig_file;
        if ($ext eq  "txt") {
            $new_name =~ s/(.*)txt/$1fastq/;
        }

        if ($TEST_DRIVE) {
            `touch $extdir/$boid\_$new_name`;
        } else {

            print "$ext_file\n";
            $newfile = "$extdir/$boid\_$new_name";
            $need_to_copy = 1;
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
