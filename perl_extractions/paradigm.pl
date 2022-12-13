use Data::Dump qw(dump);



$paradigmfile = "paradigm_standard.sma.txt";
$tagfile = "korpustags.sma.txt";



new_generate_paradigm();



#
##  COPIED FROM svn/main/gt/script/langTools/Util.pm
##

sub new_generate_paradigm {
    my %paradigms;

    generate_taglist($paradigmfile, $tagfile, \%paradigms);
    dump(%paradigms);
}


# Read the grammar for  paradigm tag list.
# Call the recursive function that generates the tag list.
sub generate_taglist {
    my ( $gramfile, $tagfile, $taglist_aref ) = @_;

    my @grammar;
    my %tags;

    if ($gramfile) {
        # Read from tag file and store to an array.
        open GRAM, "< $gramfile" or die "Cant open the file $gramfile: $!\n";
        my @tags;
        my $tag_class;
      GRAM_FILE:
        while (<GRAM>) {
            chomp;
            next if /^\s*$/;
            next if /^%/;
            next if /^$/;
            next if /^#/;

            s/\s*$//;
            push( @grammar, $_ );
        }
    }
    
    read_tags( $tagfile, \%tags );

    my @taglists;

    # Read each grammar rule and generate the taglist.
    for my $gram (@grammar) {
        my @classes = split( /\+/, $gram );
        my $pos     = shift @classes;
        my $tag     = $pos;
        my @taglist;

        generate_tag( $tag, \%tags, \@classes, \@taglist );
        push( @{ $$taglist_aref{$pos} }, @taglist );
    }
}

# Ttravel recursively the taglists and generate
# the tagsets for pardigm generation.
# The taglist is stored to the array reference $taglist_aref.
sub generate_tag {
    my ( $tag, $tags_href, $classes_aref, $taglist_aref ) = @_;

    if ( !@$classes_aref ) { push( @$taglist_aref, $tag ); return; }
    my $class = shift @$classes_aref;
    if ( $class =~ s/\?// ) {
        my $new_tag   = $tag;
        my @new_class = @$classes_aref;
        generate_tag( $new_tag, $tags_href, \@new_class, $taglist_aref );
    }

    if ( !$$tags_href{$class} ) {
        my $new_tag   = $tag . "+" . $class;
        my @new_class = @$classes_aref;
        generate_tag( $new_tag, $tags_href, \@new_class, $taglist_aref );
        return;
    }

    for my $t ( @{ $$tags_href{$class} } ) {
        my $new_tag   = $tag . "+" . $t;
        my @new_class = @$classes_aref;
        generate_tag( $new_tag, $tags_href, \@new_class, $taglist_aref );
    }
}

# Read the morphological tags from a file (korpustags.txt)
sub read_tags {
    my ( $tagfile, $tags_href ) = @_;

    # Read from tag file and store to an array.
    open TAGS, "< $tagfile" or die "Cant open the file $tagfile: $!\n";
    my @tags;
    my $tag_class;
  TAG_FILE:
    while (<TAGS>) {
        chomp;
        next if /^\s*$/;
        next if /^%/;
        next if /^$/;
        next if /=/;

        if (s/^#//) {

            $tag_class = $_;
            push( @{ $$tags_href{$tag_class} }, @tags );
            undef @tags;
            pop @tags;
            next TAG_FILE;
        }
        my @tag_a = split( /\s+/, $_ );
        push @tags, $tag_a[0];
    }

    close TAGS;
}
