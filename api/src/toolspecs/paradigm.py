import asyncio
import re
from collections import defaultdict
from subprocess import PIPE
import logging
import enum

from ..util import PartialPath

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

summary = "paradigm"
description = """
Generates the morphological paradigm from lemmas

`echo "$INPUT" | hfst-lookup -q lang-$LANG/src/analyser-gt-norm.hfstol`

The output structure is parsed and sent as json.
"""

# pipeline explained (for us non-linguists)
#
# echo word
#    just inputs the word (or words) into next program
# | tokenize tools/tokeniser-disamb-gt-desc-pmhfst
#    as far as I can tell, basically just splits each word up on a line of their own
#    (in other words, basically just replaces runs of whitespace with a single newline...?)
# | lookup analyzer-gt-desc
#    for each of those input words:
#      finds _that word_ and what its forms are, e.g (in Norwegian Bokmål)
#      input word: "bygg"
#        ->
#      bygg    bygg+N+Neu+Pl+Indef     0,000000
#      bygg    bygg+N+Neu+Sg+Indef     0,000000
#      bygg    bygge+V+Imp     0,000000
#    that is, the specific input "bygg" is 3 "actual words", namely:
#      "house" (noun, plural, as in English "many houses")
#      "house" (noun, singular, as in English "a house")
#      "house" (imperative verb of "to house", meaning "to put/give [someone] in a house",
#               example sentence: "house them now!" (meaning: "Do put them in a house, right now!")
#
# then, for each of those parts of speech, find a list of all other forms of
#   that part of speech
#   that we want to generate. For example, for verbs, we might want the
#   infinitive form ("[å] bygge"), present form ("bygger"), past form ("bygde" / "bygget"?), etc
#   Which forms we want is specified with syntax like "V+Ind+Prs" (meaning "a verb that's in
#   indicative present form").
#   To generate (or lookup?) a form of a specific verb would therefore be:
#      echo "bygge+V+Ind+Prs" | src/generator-gt-norm.hfstol
#
# so for the next step, if the user asked for a specific pos, we can just
# retrieve that list. If no specific pos is given, we select one - by
# some criteria - then use that word class to generate all forms we need.


def read_gramfile(gramfile):
    if gramfile:
        ignored_line = re.compile(r"(^[#%$])|(^\s*$)")
        with open(gramfile) as f:
            return [line.strip() for line in f if not ignored_line.match(line)]


def read_tagfile(tagfile):
    out = dict()

    tags = []
    with open(tagfile) as f:
        ignored_line = re.compile(r"(^[%$])|=|^\s*$")
        for line in f:
            line = line.strip()
            if ignored_line.search(line):
                continue

            if line.startswith("#"):
                out[line[1:]] = tags
                tags = []
            else:
                word = re.search(r"([@></\+\-\w]+)", line).group()
                tags.append(word)

    return out


def generate_tags(tag, classes, tags, taglist):
    if not classes:
        taglist.append(tag)
    else:
        current_class = classes[0]
        if current_class[-1] == "?":
            generate_tags(f"{tag}", classes[1:], tags, taglist)

        classes = classes[1:]
        current_class = current_class.replace("?", "")
        if current_class in tags:
            for variant in tags[current_class]:
                generate_tags(f"{tag}+{variant}", classes, tags, taglist)
        else:
            generate_tags(f"{tag}+{current_class}", classes, tags, taglist)


def generate_taglist(gramfile, tagfile):
    """Given a `gramfile` ("paradigm.LANG.txt") and `tagfile`
    ("korpustags.lang.txt"), generate the full list of all possible tags this
    language can have."""
    gathered = defaultdict(list)
    grammar = read_gramfile(gramfile)
    tags = read_tagfile(tagfile)

    for gram in grammar:
        tag, *classes = gram.split("+")
        gathered_taglist = []
        generate_tags(tag, classes, tags, gathered_taglist)
        gathered[tag] += gathered_taglist

    out = {}
    for basetag, taglist in gathered.items():
        out[basetag] = list(set(taglist))

    return out


def pipeline_stdout_to_json(stdout):
    return {"result": stdout}


class ParadigmSize(enum.StrEnum):
    min = "minimal"
    standard = "standard"
    full = "full"


class POS(enum.StrEnum):
    Any = "Any"
    A = "A"
    N = "N"
    V = "V"
    Adv = "Adv"
    Num = "Num"
    Pron = "Pron"


# this pipeline can accept a few more query params:
query_params = {
    "size": {
        "optional": True,
        "description": "the size of the paradigm, i.e. minimal, standard, full",
        "type": ParadigmSize,
    },
    "pos": {
        "optional": True,
        "description": "part of speech to find paradigm for, such as N, V, etc.",
        "type": POS,
    },
}


# extra files needed by this toolspec that is not referenced in the pipeline
#   TODO: fallback files.... (tagfile = korpustags.LANG.txt (or if that doesn't exist): korpustags.txt)
extra_files = {
    "sma": {
        "paradigm_full.txt": PartialPath("test/data/paradigm_full.sma.txt"),
        "paradigm_min.txt": PartialPath("test/data/paradigm_min.sma.txt"),
        "paradigm_standard.txt": PartialPath("test/data/paradigm_standard.sma.txt"),
        "korpustags.txt": PartialPath("test/data/korpustags.sma.txt"),
    },
    "sme": {
        "paradigm_full.txt": PartialPath("test/data/paradigm_full.sme.txt"),
        "paradigm_min.txt": PartialPath("test/data/paradigm_min.sme.txt"),
        "paradigm_standard.txt": PartialPath("test/data/paradigm_standard.sme.txt"),
        "korpustags.txt": PartialPath("test/data/korpustags.sme.txt"),
    },
    "nob": {
        # TODO these files are copied from sme, just to have some test data!
        "paradigm_full.txt": PartialPath("test/data/paradigm_full.nob.txt"),
        "paradigm_min.txt": PartialPath("test/data/paradigm_min.nob.txt"),
        "paradigm_standard.txt": PartialPath("test/data/paradigm_standard.nob.txt"),
        "korpustags.txt": PartialPath("test/data/korpustags.nob.txt"),
    },
    "*": {
        "generator-gt-norm.hfstol": PartialPath("src/generator-gt-norm.hfstol"),
    }
}


def determine_is_derivation(tags):
    return "Der" in tags


def determine_is_compound(tags):
    """Given a tag list, determine if it it is a compound"""
    # from original source (smi.cgi)
    #   if tags contains a '#', and does not start with something else than '+'
    #   followed by '#', in that case it is a compound
    #   if ($anl =~/\#/ && $anl !~ /^[^\+]+\#[^\#]+$/) {
    # TODO is this correct, then?
    return "#" in tags and not tags.startswith("+#")


def find_poses_from_analyses(analyses):
    out = {}
    # analyses is a string with many lines, coming directly from 'hfst-lookup'
    for line in analyses.split("\n"):
        lemma, tags, weight = line.split("\t")
        is_derivation = determine_is_derivation(tags)
        is_compound = determine_is_compound(tags)

        match (is_derivation, is_compound):
            case (False, False):
                # not a derivation, nor a compound
                _lemma, pos, *_ = tags.split("+")
                return {pos: {"rank": 1, "results": None}}
            case (False, True):
                # not a derivation, but is a compound
                #  my $anltmp = $anl;
                #  # Note: Is the following line needed when we negate /Der/ 15 lines further up?
                #  $anltmp =~ s/\#\+Der\d\+Der\//\#/g;
                #  $anltmp =~ /^(.*\#.*?)\+(.*)$/;
                #  $anltmp = $1;
                #  my $line2 = $2;
                #  # !!! ANDERS: Where is this defined? I can't find it!
                #  format_compound(\$anltmp, \$line2, \$word);
                #  $fulllemma=$anltmp;
                #  ($anlpos) = split(/\+/, $line2);
                #  ($anllemma = $anltmp) =~ s/^.*\#([^\#]+)$/$1/;
                #  #print FH "$anltmp ja $line2 ja $anllemma ja $anlpos\n";
                m = re.match(r"^(.*\#.*?)\+(.*)$", tags)
                if not m:
                    raise Exception("don't think should have happened")
                # anltmp = m.group(1)
                # line2 = m.group(2)
                # format_compound(anltmp, line2, word)

                return out
            case (True, _):
                # is derivation, compound can be anything (true or false)
                pass

    return out


# all paradigms per lang, per paradigmmode
# paradigm_files[lang][mode] = ...
PARADIGM_FILES = defaultdict(dict)


def on_startup(lang, extra_files):
    """for all languages, find which paradigm sizes they can do (if any), and
    pre-generate the tags (for all langs, for all modes)"""
    PARADIGM_SIZES = {"min": "minimal", "standard": "standard", "full": "full"}
    files = extra_files[lang]
    for abbreviation, size in PARADIGM_SIZES.items():
        gramfile = files.get(f"paradigm_{abbreviation}.txt")
        tagfile = files.get("korpustags.txt")

        if gramfile and tagfile:
            logger.info(f"generating taglist for {lang} {size}")
            PARADIGM_FILES[lang][abbreviation] = generate_taglist(gramfile, tagfile)


async def generate_paradigm(analyses, lang, query_params=None):
    if query_params is None:
        query_params = {}

    pos = query_params.get("pos", "Any")
    size = query_params.get("size", "standard")

    # fast path: specific pos was given
    if pos != "Any":
        try:
            paradigmfile = PARADIGM_FILES[lang][size.name][pos]
        except KeyError as e:
            return {"error": f"lang, size or pos not found ({e})"}

        return await call_para(analyses, lang, paradigmfile)

    # slow path: pos not given
    poses = find_poses_from_analyses(analyses)

    # make sure the "primary" we selected is marked somehow..
    # select_best_poses
    # if lemma == input we were given, then that is the primary,
    # otherwise select the first one we found (possible to do better?)

    # then, do paradigm generation for all poses we found,
    # but make sure to mark the "primary" we selected specifically in the output

    # primary pos we selected: the first one in the list, and dictionary
    # preserves order? Does it necessarily preserve order when JSONified and
    # reconstructed by js? probably not..
    for pos, entry in poses.items():
        try:
            paradigmfile = PARADIGM_FILES[lang][size][pos]
        except KeyError:
            return {"error": "lang, mode or pos not found"}

        entry["results"] = await call_para(analyses, lang, paradigmfile)

    return poses


async def call_para(analyses, lang, paradigmfile):
    # find the word again from analysis
    word = None
    for line in analyses.split("\n"):
        try:
            word, _tags, _weight = line.split("\t")
        except ValueError:
            continue
        else:
            break

    # for each entry in the paradigm file (for this pos),
    # make a string like "WORD+{para}", where para is "N+..." for all variants
    # we want (and all variants depends on which "mode" we're doing paradigm for)
    input = "\n".join(f"{word}+{para}" for para in paradigmfile)
    input = input.encode("utf-8")

    # TODO replace with hfst
    # now run the subprocess call
    # echo gen_input | hfst-lookup src/generator-gt-norm.hfstol
    generator_gt_norm_hfstol = extra_files[lang]["generator-gt-norm.hfstol"]
    subp = await asyncio.create_subprocess_exec(
        *["hfst-lookup", "-q", generator_gt_norm_hfstol],
        stdin=PIPE, stdout=PIPE, stderr=PIPE,
    )

    stdout, stderr = await subp.communicate(input)

    # TODO error checking (if anything is on stderr, for example)
    reslist = []
    stdout = stdout.decode("utf-8")
    for line in stdout.split("\n"):
        try:
            paradigm, word_form, weight = line.split("\t")
        except ValueError:
            # could not unpack 3
            pass
        else:
            if weight != "inf":
                reslist.append([paradigm, word_form])

    return reslist


pipeline = [
    [
        "hfst-tokenize",
        "-q", "--beam=0",
        PartialPath("tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"),
    ],
    [
        "hfst-lookup",
        "-q", "--beam=0",
        PartialPath("src/analyser-gt-desc.hfstol"),
    ],
    generate_paradigm,
    # pipeline_stdout_to_json,
]
