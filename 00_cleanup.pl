#!/usr/bin/perl
use strict;

sub recursive_clean (@_);


my $fromdir = "/mnt/bodamer01";

-e $fromdir || die "$fromdir not found.\n";
-d $fromdir || die "$fromdir does not seem to be a directory.\n";

my $TEST_DRIVE = 0;

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
        foreach my $subdir (@subs) {
            (-d "$thing/$subdir") || next;
            recursive_clean ("$thing/$subdir");
            my $new_name = $subdir;
            $new_name =~ s/ File/ file/g;
            $new_name =~ s/\s+/_/g;
            $new_name =~ s/[\(\)]/_/g;
            $new_name =~ s/__/_/g;
            if ($new_name ne $subdir) {
                my $path_no_space = $thing;   $path_no_space =~ s/([\s\(\)])/\\$1/g;
                my $subdir_no_space = $subdir;  $subdir_no_space =~ s/([\s\(\)])/\\$1/g;
                my $cmd = "mv $path_no_space/$subdir_no_space $path_no_space/$new_name";
                if ($TEST_DRIVE) {
                    print "$cmd\n";
                } else {
                    system ($cmd) && die "error running $cmd\n";
                }
            }
    	}
    }

    return;
}