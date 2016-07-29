 #!/usr/bin/perl
use data_mgmt_utils_pl::md5 qw(get_md5sum);
$ext_file = "/home/ivana/scratch/1568419.jv.vcf.bz2";
($md5sum, $dummy) = get_md5sum (0, $ext_file);
print "$md5sum\n$dummy\n";