
open(F,"dict.txt");

while(<F>) {
	$word = (split(/\s/))[0];
	if (length($word) == 12) {
		print uc($word)."\n";
	}
}

close F;