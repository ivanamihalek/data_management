#!/usr/bin/perl
use strict;
sub recursive_clean (@_);


@ARGV==1 || die "Usage: $0 <fromdir>\n";
my $fromdir = $ARGV[0];

if ($fromdir eq  "/mnt/bodamer02") {
} elsif ($fromdir eq  "/mnt/bodamer01"){
} else {
    die "Unexpected fromdir: $fromdir\n";
}





-e $fromdir || die "$fromdir not found.\n";
-d $fromdir || die "$fromdir does not seem to be a directory.\n";

my $TEST_DRIVE = 1;

my @listing_level_1 = split "\n", `ls $fromdir`;

my @cases  = ();

foreach ( @listing_level_1 ) {
    if( -d "$fromdir/$_") {
       /^BO/  && push @cases, $_;
    }
}

foreach my $case (@cases) {
    print "$case\n";
    recursive_clean ("$fromdir/$case");
}

#######################################
sub recursive_clean (@_) {

    my $thing = $_[0];

    if (-d $thing) {
        my $thing_no_space = $thing;
        $thing_no_space =~ s/([\s\(\)])/\\$1/g;
        my @subs = split "\n", `ls $thing_no_space`;
        
        foreach my $subthing (@subs) {
            if ($subthing =~ /copy/) {
                print "$subthing\n";
            }
            my $new_name = $subthing;
            $new_name =~ s/ File/ file/g;
            $new_name =~ s/\s+/_/g;
            $new_name =~ s/[\(\)]/_/g;
            $new_name =~ s/__/_/g;
            if ($new_name ne $subthing) {
                my $path_no_space = $thing;   $path_no_space =~ s/([\s\(\)])/\\$1/g;
                my $subthing_no_space = $subthing;  $subthing_no_space =~ s/([\s\(\)])/\\$1/g;
                my $cmd = "mv $path_no_space/$subthing_no_space $path_no_space/$new_name";
                if ($TEST_DRIVE) {
                    print "$cmd\n";
                } else {
                    $cmd =~ /copy/ && print "$cmd\n";
                    system ($cmd) && die "error running $cmd\n";
                }
            }
            # if the sub-thing is a directory, descend
            (-d "$thing/$subthing") && recursive_clean ("$thing/$subthing");

    	}
    }

    return;
}