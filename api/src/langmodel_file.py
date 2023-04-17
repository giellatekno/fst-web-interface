from pathlib import Path


def generator_len(gen):
    n = 0
    for _ in gen:
        n += 1
    return n


class LangmodelFile:
    """A language model file that a tool may require to run."""

    def __init__(self, name, path, requires_build=True, buildflags=None):

        # name that the code will refer to the file as, usually just the
        # name of the file
        self.name = name

        # where this file is located in the repository
        # can be a string, or a function of repository name, for files that
        # are named differently in different repositories
        self.path = path

        # not all files requires building, some files are included in the
        # source repository directly
        self.requires_build = requires_build

        # list of build flags, if it needs to be built
        self.buildflags = [] if buildflags is None else buildflags

    def __repr__(self):
        return (
            "LangmodelFile { name="
            f"{self.name}, path={self.path}, "
            f"requires_build={self.requires_build}"
            " }"
        )

    def resolve_path(self, basepath, lang=None):
        if callable(self.path):
            if lang is None:
                raise Exception(
                    "LangModelFile.resolve_path(): self.path is callable, "
                    "but no `lang` argument was passed to resolve it"
                )
            else:
                return Path(basepath) / Path(self.path(lang))
        else:
            return Path(basepath) / Path(self.path)

    def copy(self):
        return LangmodelFile(
            self.name, self.path, self.requires_build, list(self.buildflags))


TOKENISER_DISAMB_GT_DESC_PMHFST = LangmodelFile(
    name="tokeniser-disamb-gt-desc.pmhfst",
    path="tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst",
    buildflags=["enable-tokenisers"],
)

ANALYSER_GT_DESC_HFSTOL = LangmodelFile(
    name="analyser-gt-desc.hfstol",
    path="src/analyser-gt-desc.hfstol",
)

GENERATOR_GT_NORM_HFSTOL = LangmodelFile(
    name="generator-gt-norm.hfstol",
    path="src/generator-gt-norm.hfstol",
)

HYPHENATOR_GT_DESC_HFSTOL = LangmodelFile(
    name="hyphenator-gt-desc.hfstol",
    path="tools/hyphenators/hyphenator-gt-desc.hfstol",
    buildflags=["enable-fst-hyphenator"],
)

DISAMBIGUATOR_CG3 = LangmodelFile(
    name="disambiguator.cg3",
    path="src/cg3/disambiguator.cg3",
    requires_build=False,
)

DEPENDENCY_CG3 = LangmodelFile(
    name="dependency.cg3",
    path="src/cg3/dependency.cg3",
    requires_build=False,
)

KORP_CG3 = LangmodelFile(
    name="korp.cg3",
    path="src/cg3/korp.cg3",
    requires_build=False,
)

TRANSCRIPTOR_NUMBERS_DIGIT2TEXT_FILTERED_LOOKUP_HFSTOL = LangmodelFile(
    name="transcriptor-numbers-digit2text.filtered.lookup.hfstol",
    path="src/transcriptions/transcriptor-numbers-digit2text.filtered.lookup.hfstol"
)

TXT2IPA_COMPOSE_HFST = LangmodelFile(
    name="txt2ipa.compose.hfst",
    path="src/phonetics/txt2ipa.compose.hfst",

    # building tts requires phonetic and tokenisers
    buildflags=["enable-phonetic", "enable-tts", "enable-tokenisers"],
)

PARADIGM_MIN_TXT = LangmodelFile(
    name="paradigm_min.txt",
    path=lambda lang: f"test/data/paradigm_min.{lang}.txt",
    requires_build=False,
)

PARADIGM_STANDARD_TXT = LangmodelFile(
    name="paradigm_standard.txt",
    path=lambda lang: f"test/data/paradigm_standard.{lang}.txt",
    requires_build=False,
)

PARADIGM_FULL_TXT = LangmodelFile(
    name="paradigm_full.txt",
    path=lambda lang: f"test/data/paradigm_full.{lang}.txt",
    requires_build=False,
)

KORPUSTAGS_TXT = LangmodelFile(
    name="korpustags.txt",
    path=lambda lang: f"test/data/korpustags.{lang}.txt",
    requires_build=False,
)


class LangmodelFiles:
    """A collection of LangmodelFile's."""

    def __init__(self):
        self.files = {}

    def add(self, file):
        if file.name in self.files:
            raise Exception(
                f"Duplicate language model files with name '{file.name}'")

        self.files[file.name] = file

    def mark_in_apertium(self, files):
        """Mark the set of files `files` as present in apertium."""
        for f in files:
            if f in self.files:
                self.files[f].in_apertium = True

    def missing_files(self):
        # Only used by builder
        for name, file in self.files.items():
            in_apertium = hasattr(file, "in_apertium") and file.in_apertium
            in_repo = not file.requires_build
            if not in_repo and not in_apertium:
                yield file.name

    def needs_build(self):
        # Only used by builder
        return generator_len(self.missing_files()) > 0

    def determine_configure_flags(self):
        """Determine flags to pass to ./configure in order to compile the
        remaining of these language model files."""
        flags = set()
        for name in self.missing_files():
            file = self.files[name]
            flags |= set(file.buildflags)

        return flags

    def copy(self):
        inst = LangmodelFiles()
        for name, file in self.files.items():
            inst.files[name] = file.copy()
        return inst


langmodel_files = LangmodelFiles()

langmodel_files.add(TOKENISER_DISAMB_GT_DESC_PMHFST)
langmodel_files.add(ANALYSER_GT_DESC_HFSTOL)
langmodel_files.add(GENERATOR_GT_NORM_HFSTOL)
langmodel_files.add(HYPHENATOR_GT_DESC_HFSTOL)
langmodel_files.add(DISAMBIGUATOR_CG3)
langmodel_files.add(DEPENDENCY_CG3)
langmodel_files.add(KORP_CG3)
langmodel_files.add(TRANSCRIPTOR_NUMBERS_DIGIT2TEXT_FILTERED_LOOKUP_HFSTOL)
langmodel_files.add(TXT2IPA_COMPOSE_HFST)

langmodel_files.add(PARADIGM_MIN_TXT)
langmodel_files.add(PARADIGM_STANDARD_TXT)
langmodel_files.add(PARADIGM_FULL_TXT)
langmodel_files.add(KORPUSTAGS_TXT)
