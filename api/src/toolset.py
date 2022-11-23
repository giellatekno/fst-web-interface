import subprocess
from collections import defaultdict

from .config import GTLANGS
from .util import PartialPath

from .toolspecs import dependency as dependency_spec
from .toolspecs import disambiguate as disambiguate_spec
from .toolspecs import generate as generate_spec
from .toolspecs import hyphenate as hyphenate_spec
from .toolspecs import paradigm as paradigm_spec
from .toolspecs import transcribe as transcribe_spec


def parse_needed_files(pipeline_spec):
    """Parse out all needed files from a given pipeline spec."""
    needed = set()

    for prog in pipeline_spec:
        if not isinstance(prog, list):
            continue
        for entry in prog:
            if isinstance(entry, PartialPath):
                needed.add(entry.p)

    return needed


def resolve_pipeline(pipeline_spec, available_files):
    """Return a new pipeline from a pipeline spec, with all
    PartialPath's resolved to their corresponding real file paths.
    `available_files` is a mapping from PartialPaths to actual real file paths.
    If the spec contains any PartialPath for which there is no corresponding
    mapping in `available_files`, return None."""
    resolved_pipeline = []
    for entry in pipeline_spec:
        newprog = []
        if callable(entry):
            # functions are just passed through as is
            resolved_pipeline.append(entry)
            continue

        # otherwise, it's a list, so it's a program to run with subprocess.run(),
        # so we must replace PartialPath's with real ones
        for s in entry:
            if isinstance(s, str):
                # strings are just passed through
                newprog.append(s)
            elif isinstance(s, PartialPath):
                partial_path = s.p
                real_path = available_files.get(partial_path)
                if real_path is None:
                    # Found a wanted path that we do not have
                    return None
                newprog.append(real_path)
        resolved_pipeline.append(newprog)

    return resolved_pipeline


def gather_available_files(wanted_files):
    """Take a set of all wanted files as input,
    and return a mapping of which files are available for each language found
    in $GTLANGS."""
    files = defaultdict(dict)

    for p in GTLANGS.glob("lang-*"):
        lang = p.name[5:]

        for wanted_file in wanted_files:
            full_path = p / wanted_file
            if full_path.is_file():
                files[lang][wanted_file] = full_path

    return files


class Tool:
    def __init__(self, spec):
        # spec as given in toolspecs/<file>.py
        self.spec = spec

        # list of langauges this tool supports
        self.langs = []

        # get a pipeline for a given language
        self.pipeline_for = {}

        self.pipeline_stdout_to_json = spec.pipeline_stdout_to_json

    def run_pipeline(self, lang, input):
        final_output = { "input": input }

        for prog in self.pipeline_for[lang]:
            if callable(prog):
                try:
                    input = prog(input)
                except Exception as e:
                    final_output["error"] = str(e)
                    return final_output
            else:
                res = subprocess.run(prog, input=input, text=True, capture_output=True)
                if res.stdout != "":
                    input = res.stdout
                else:
                    final_output["error"] = res.stderr
                    return final_output

        final_output["result"] = input
        return final_output


class Tools:
    def __init__(self):
        # keep a referece to every Tool by tool name
        self.tools = {}

        # a set of all files we want
        self.all_wanted_files = set()

        # mapping of tool name -> capabilities (languages)
        self.capabilities = defaultdict(list)

    def add(self, spec):
        specname = spec.__name__.split(".")[-1]

        self.all_wanted_files |= parse_needed_files(spec.pipeline)

        tool = Tool(spec)
        self.tools[specname] = tool
        return tool

    def resolve_pipelines(self, available_files):
        for toolname, tool in self.tools.items():
            for lang, files in available_files.items():
                resolved_pipeline = resolve_pipeline(
                    tool.spec.pipeline, available_files[lang]
                )
                if resolved_pipeline:
                    tool.langs.append(lang)
                    tool.pipeline_for[lang] = resolved_pipeline
                    self.capabilities[lang].append(toolname)

    def print_available_tools_by_language(self):
        """Prints a list of languages, and which tools are available for each of those."""
        for lang, tools in self.capabilities.items():
            print(f"Available tools for language '{lang}': {', '.join(tools)}")

    def print_available_langs_by_tool(self):
        """Prints a list of tools, and which languages are available for each of those."""
        pass



tools = Tools()

dependency = tools.add(dependency_spec)
disambiguate = tools.add(disambiguate_spec)
generate = tools.add(generate_spec)
hyphenate = tools.add(hyphenate_spec)
paradigm = tools.add(paradigm_spec)
transcribe = tools.add(transcribe_spec)

available_files = gather_available_files(tools.all_wanted_files)
tools.resolve_pipelines(available_files)

tools.print_available_tools_by_language()
# alternatively:
#tools.print_available_langs_by_tool()

