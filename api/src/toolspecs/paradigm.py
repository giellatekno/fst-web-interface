import asyncio
import re
from collections import defaultdict
from subprocess import PIPE
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

from ..util import PartialPath

summary = "paradigm"
description = """
Generates the morphological paradigm from lemmas

`echo "$INPUT" | hfst-lookup -q lang-$LANG/src/generator-gt-norm.hfstol`

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
# then, for each of those word classes, find a list of all other forms of that word class
#   that we want to generate. For example, for verbs, we might want the
#   infinitive form ("[å] bygge"), present form ("bygger"), past form ("bygde" / "bygget"?), etc
#   Which forms we want is specified with syntax like "V+Ind+Prs" (meaning "a verb that's in
#   indicative present form").
#   To generate (or lookup?) a form of a specific verb would therefore be:
#      echo "bygge+V+Ind+Prs" | src/generator-gt-norm.hfstol
#  
# so for the next step, if the user asked for a specific word class, we can just retrieve
# that list. If no specific word class is given, we select one - by which criteria I currently
# don't know - then use that word class to generate all forms we need.

def read_gramfile(gramfile):
    if gramfile:
        ignored_line = re.compile(r"(^[#%$])|(^\s*$)")
        with open(gramfile) as f:
            return [ line.strip() for line in f if not ignored_line.match(line) ]


def read_tagfile(tagfile):
    out = dict()

    tags = []
    with open(tagfile) as f:
        ignored_line = re.compile(r"(^[%$])|=|^\s*$")
        for line in f:
            line = line.strip()
            if ignored_line.search(line): continue

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
    """Given a `gramfile` ("paradigm.LANG.txt") and `tagfile` ("korpustags.lang.txt"),
    generate the full list of all possible tags this language can have."""
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
    return { "result": stdout }


# this pipeline can accept a few more query params:
query_params = {
    "mode": {
        "optional": True,
        "description": "the size of the paradigm, i.e. minimal, standard, full",
    },
    "word_class": {
        "optional": True,
        "description": "word class to find paradigm for, such as N, V, etc.",
    },
}

# we need to know which LANG this is, to find the paradigm files
# but all of this can probably be done when we startup the app
#paradigmfiles = dict(
#    minimal="paradigm_min.LANG.txt",
#    standard="paradigm_standard.LANG.txt",
#    full="paradigm_full.LANG.txt",
#)
#if mode: paradigmfile = paradigmfiles[mode]
#if not mode or paradigmfile does not exist: paradigmfile = "paradigm.LANG.txt"
#if paradigmfile does not exist: paradigmfile = "paradigm.txt"

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
        # TODO for now, intentionally wrong to provoke the error
        "paradigm_full.txt": PartialPath("test/data/paradigm_full.sme.txt"),
        "paradigm_min.txt": PartialPath("test/data/paradigm_min.sme.txt"),
        "paradigm_standard.txt": PartialPath("test/data/paradigm_standard.sme.txt"),
        "korpustags.txt": PartialPath("test/data/korpustags.sme.txt"),
    },
    "*": {
        "generator-gt-norm.hfstol": PartialPath("src/generator-gt-norm.hfstol"),
    }
}

PARADIGM_MODES = { "min": "minimal", "standard": "standard", "full": "full" }

def get_extra_files(lang):
    return { **extra_files["*"], **extra_files.get(lang, {}) }

# all paradigms per lang, per paradigmmode
# paradigm_files[lang][mode] = ...
PARADIGM_FILES = defaultdict(dict)

def on_startup(lang):
    # for all languages, find which paradigm modes they can do (if any), and
    # pre-generate the tags (for all langs, for all modes)
    files = get_extra_files(lang)
    for abbr, mode in PARADIGM_MODES.items():
        gramfile = files.get(f"paradigm_{abbr}.txt")
        tagfile = files.get("korpustags.txt")

        if gramfile and tagfile:
            logger.info(f"generating taglist for {lang} {mode}")
            PARADIGM_FILES[lang][abbr] = generate_taglist(gramfile, tagfile)


async def generate_paradigm(analyses, lang, query_params={}):
    #print(f"generate_paradigm(). {lang=}, {query_params=}")
    word_class = query_params.get("word_class", "Any")
    mode = query_params.get("mode", "standard")

    if word_class == "Any":
        # TODO If word class is explicitly set to Any, or not given,
        # we want to select a word class by some metric, and primarily
        # show that output, but also give a "you could also have meant"-box,
        # showing on the side
        # TODO TEMP for now..
        word_class = "N"

    try:
        # TODO word_class is supposed to be optional, so if it isn't given, we
        # must select one, using some method.. (found in smi.pl)
        paradigmfile = PARADIGM_FILES[lang][mode][word_class]
    except KeyError:
        return { "error": "lang, mode or word_class not found" }

    return await call_para(analyses, lang, paradigmfile)

    #if word_class:
    #    paradigm_list = paradigm_lists[word_class]
    #    call_para(input, paradigm_list)
    #else:
    #    for anl in analyses.split("\n"):
    #        if "+?" in anl:
    #            continue
    #        lemma, anl = anl.split(" ")
    #        if "Der" not in anl:
    #            # not a derivation
    #            pass
    #        else:
    #            # handle derivations separately here
    #            pass

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

    # for each entry in the paradigm file (for this word class),
    # make a string like "WORD+{para}", where para is "N+..." for all variants
    # we want (and all variants depends on which "mode" we're doing paradigm for)
    input = "\n".join(f"{word}+{para}" for para in paradigmfile)
    input = input.encode("utf-8")

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
    pipeline_stdout_to_json,
]


