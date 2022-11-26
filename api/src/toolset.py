import asyncio
from asyncio.subprocess import PIPE
import subprocess
import inspect
from typing import Any
from collections import defaultdict
import logging

from .config import GTLANGS
from .util import PartialPath

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


def find_response_model(pipeline_spec):
    last_step = pipeline_spec[-1]

    # the last step is a list, so we can't say more than that
    # the response model is a string
    if isinstance(last_step, list):
        return str

    # find signature of function
    sig = inspect.signature(last_step)
    return_annotation = sig.return_annotation
    if return_annotation is inspect.Signature.empty:
        return Any
    else:
        return return_annotation


def gather_available_files(wanted_files):
    """Take a set of all wanted files as input,
    and return a mapping of which files are available for each language found
    in $GTLANGS."""
    files = defaultdict(dict)

    if GTLANGS is None:
        return files

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
        self.name = spec.__name__.split(".")[-1]

        # which GTLANGS-dependent files does this tool
        # want (rely on)?
        self.wanted_files = parse_needed_files(spec.pipeline)

        # list of langauges this tool supports
        self.langs = []

        # get a pipeline for a given language
        self.pipeline_for = {}

        # will be set by the Tools when loading the tool,
        # and shown on the openapi docs
        self.description = ""
        self.summary = ""

        # response model of this tool defaults to Any
        self.response_model = Any

    async def run_pipeline(self, lang, input):
        final_output = { "input": input }

        if "*" in self.pipeline_for:
            pipeline = self.spec.pipeline
        else:
            pipeline = self.pipeline_for[lang]

        for prog in pipeline:
            if callable(prog):
                try:
                    input = prog(input)
                except Exception as e:
                    final_output["error"] = str(e)
                    return final_output
            else:
                subp = await asyncio.create_subprocess_exec(
                        *prog, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout, stderr = await subp.communicate(input.encode("utf-8"))
                stdout = stdout.decode("utf-8")
                if stdout != "":
                    input = stdout
                else:
                    final_output["error"] = stderr.decode("utf-8")
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
        spec_dict = dict(inspect.getmembers(spec))

        tool = Tool(spec)

        self.all_wanted_files |= tool.wanted_files
        tool.description = spec_dict.get("description", "")
        tool.summary = spec_dict.get("summary", "")
        tool.response_model = find_response_model(spec_dict["pipeline"])

        self.tools[specname] = tool
        return tool

    def resolve_pipelines(self):
        available_files = gather_available_files(self.all_wanted_files)

        for toolname, tool in self.tools.items():
            if len(tool.wanted_files) == 0:
                logging.error(f"tool {toolname} is non-fst (no requirements on GTLANGS-specific files")
                # This tool doesn't want any GTLANGS files, so just pass the
                # pipeline through (it also means it's not dependant on "langs")
                tool.pipeline_for["*"] = tool.spec.pipeline
                continue

            for lang, files in available_files.items():
                resolved_pipeline = resolve_pipeline(
                    tool.spec.pipeline, available_files[lang]
                )
                if resolved_pipeline:
                    tool.langs.append(lang)
                    tool.pipeline_for[lang] = resolved_pipeline
                    self.capabilities[lang].append(toolname)
                else:
                    tool.pipeline_for = None

    def print_available_tools_by_language(self):
        """Prints a list of languages, and which tools are available for each of those."""
        for lang, tools in self.capabilities.items():
            print(f"Available tools for language '{lang}': {', '.join(tools)}")

    def print_available_langs_by_tool(self):
        """Prints a list of tools, and which languages are available for each of those."""
        pass


tools = Tools()

from . import toolspecs

# add all tools (modules) found in /toolspecs to the
# global `tools` object, and also add all the newly
# created `Tool` object to the global (module-level) namespace
for name, spec in inspect.getmembers(toolspecs):
    if name.startswith("__"):
        continue

    tool = tools.add(spec)
    globals()[name] = tool

tools.resolve_pipelines()

tools.print_available_tools_by_language()
# alternatively:
#tools.print_available_langs_by_tool()

