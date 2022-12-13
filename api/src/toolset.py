import asyncio
from asyncio.subprocess import PIPE
import subprocess
import shlex
import inspect
from itertools import islice
from typing import Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

from .config import GTLANGS
from .util import PartialPath


def noop(*args, **kwargs): pass


def dict_first_value(d):
    """Extracts the "first" value of a dictionary. "First" being the
    first entry in d.values()."""
    return list(islice(d.values(), 1))[0]


def fn_takes_query_params(f):
    return "query_params" in inspect.signature(f).parameters


def find_needed_files(all_pipelines, extra_files):
    """Find all needed files from a pipeline."""
    needed = set()

    for _lang, pipeline in all_pipelines.items():
        for program in pipeline:
            if not isinstance(program, list):
                continue
            for entry in program:
                if isinstance(entry, PartialPath):
                    needed.add(entry.p)

    return needed


def resolve_pipeline(wanted_lang, pipelines, available_files):
    """From the dictionary of available files, find a matching file for
    partial_path, searching first for the specific lang, and otherwise
    in the general section."""

def normalize_pipelines(pipelines):
    """Turns a pipeline spec of just a single list into one with just that
    one single list as the default (catchall) pipeline. If the pipeline already
    is a dict, we just return it as is."""
    if isinstance(pipelines, list):
        return {"*": pipelines}
    else:
        return pipelines


def resolve_pipelines(pipelines: dict[str, list], available_files: dict[str, str]):
    """Replace all occurences of PartialPaths in all pipelines with the
    real file path, found in the `available_files` dictionary. If the
    PartialPath is not available, that pipeline will be removed, as it cannot
    run due to missing files."""
    resolved_pipelines = {}

    for avail_lang, avail_files in available_files.items():
        pipeline = pipelines.get(avail_lang)
        if not pipeline:
            pipeline = pipelines.get("*")
            if not pipeline:
                # no pipelines for this tool, for this language
                break

        new_pipeline = []
        for program in pipeline:
            if callable(program):
                new_pipeline.append(program)
            else:
                new_program = []
                for s in program:
                    if isinstance(s, str):
                        new_program.append(s)
                    elif isinstance(s, PartialPath):
                        partial_path = s.p
                        found_file = avail_files.get(partial_path)
                        if found_file:
                            new_program.append(found_file)
                        else:
                            new_program = None
                            break

                if new_program is not None:
                    new_pipeline.append(new_program)
                else:
                    new_pipeline = None
                    break

        if new_pipeline is not None:
            resolved_pipelines[avail_lang] = new_pipeline

    assert "*" not in resolved_pipelines
    return resolved_pipelines


def find_response_model(all_pipelines):
    """Find the response model of all pipelines. All pipelines must have the
    same response model, because the route in fastapi is defined by the
    first one we find, and any other pipeline that does not share the
    same response model, will fail to verify on return, and lead to a crash."""
    last_step = dict_first_value(all_pipelines)[-1]
    if isinstance(last_step, list):
        return str
    elif callable(last_step):
        return_annotation = inspect.signature(last_step).return_annotation
        if return_annotation is inspect.Signature.empty:
            return Any
        else:
            return return_annotation


def get_repo_info(path):
    # first try to read this info from REPO_INFO
    # it will be made when deploying
    commithash, commitdate = None, None
    try:
        with open(f"{path}/REPO_INFO") as f:
            commithash, commitdate = f.read().strip().split(" ")
    except FileNotFoundError:
        # okay, try to run git command there, then
        env = dict(GIT_DIR = f"{path}/.git")
        prog = shlex.split("git log -n 1 --format=format:\"%h %cI\"")
        try:
            res = subprocess.run(prog, capture_output=True, env=env)
        except FileNotFoundError:
            return None, None
        else:
            stdout = res.stdout.strip().decode("utf-8").split(" ")
            commithash = stdout[0]
            commitdate = " ".join(stdout[1:])

    return commithash, commitdate


def gather_available_files(wanted_files):
    """Take a set of all wanted files as input,
    and return a mapping of which files are available for each language found
    in $GTLANGS."""
    available_files = defaultdict(dict)

    if GTLANGS is None:
        return available_files, (None, None)

    repos_info = {}
    for p in GTLANGS.glob("lang-*"):
        lang = p.name[5:]
        repos_info[lang] = commithash, commitdate = get_repo_info(p)

        for wanted_file in wanted_files:
            full_path = p / wanted_file
            if full_path.is_file():
                available_files[lang][wanted_file] = full_path
            else:
                logger.warn(f"lang-{lang} wants file {wanted_file}, but it was not found")

    return available_files, repos_info


class Tool:
    def __init__(self, spec):
        # spec as given in toolspecs/<file>.py
        self.spec = spec
        self.name = spec.__name__.split(".")[-1]
        spec_dict = dict(inspect.getmembers(spec))
        self.description = spec_dict.get("description", "(no description given)")
        self.summary = spec_dict.get("summary", "(no summary given)")
        self.pipelines = normalize_pipelines(spec_dict["pipeline"])
        self.query_params = spec_dict.get("query_params", {})
        self.extra_files = spec_dict.get("extra_files", {})
        self.wanted_files = find_needed_files(self.pipelines, spec_dict.get("extra_files"))
        self.response_model = find_response_model(self.pipelines)
        
        if "on_startup" not in spec_dict:
            self.on_startup = noop
        else:
            on_startup = spec_dict["on_startup"]
            if not callable(on_startup):
                logger.error(f"toolspec/{self.name}: on_startup must be a function")
                on_startup = noop
            self.on_startup = on_startup

    def resolve_extra_files(self):
        for p in GTLANGS.glob("lang-*"):
            lang = p.name[5:]

            if "*" in self.extra_files:
                star_updates = {}
                for entry, partial_path in self.extra_files["*"].items():
                    file_path = p / partial_path.p
                    if file_path.is_file():
                        star_updates[entry] = file_path
                    else:
                        logger.warn(f"lang-{lang} wants file {partial_path.p}, but it was not found")
                        star_updates[entry] = None
                    if lang in self.extra_files:
                        self.extra_files[lang].update(star_updates)

            if lang in self.extra_files:
                updates = {}
                for entry, partial_path in self.extra_files[lang].items():
                    if not isinstance(partial_path, PartialPath):
                        continue
                    file_path = p / partial_path.p
                    if file_path.is_file():
                        updates[entry] = file_path
                    else:
                        updates[entry]= None
                        logger.warn(f"lang-{lang} wants file {partial_path.p}, but it was not found")
                self.extra_files[lang].update(updates)


    async def run_pipeline(self, lang, input, query_params=None):
        final_output = { "input": input }

        pipeline = self.pipelines.get(lang)

        for prog in pipeline:
            if callable(prog):
                try:
                    if inspect.iscoroutinefunction(prog):
                        print("will run an async function")
                        if fn_takes_query_params(prog):
                            input = await prog(input, str(lang), query_params=query_params)
                        else:
                            input = await prog(input)
                    else:
                        if fn_takes_query_params(prog):
                            input = prog(input, str(lang), query_params=query_params)
                        else:
                            input = prog(input)
                except Exception as e:
                    logger.exception("Exception in pipeline python step")
                    final_output["error"] = "Python step of pipeline threw unhandled exception"
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
        self.tools = {}
        self.all_wanted_files = set()

        # mapping of tool name -> list of langs supported
        self.capabilities = defaultdict(list)

        # mapping of lang -> tuple of commithash, commitdate
        self.repos_info = None

    def add(self, spec):
        tool = Tool(spec)
        self.tools[tool.name] = tool

        self.all_wanted_files |= tool.wanted_files

        return tool

    def resolve_pipelines(self):
        available_files, repos_info = gather_available_files(self.all_wanted_files)
        self.repos_info = repos_info

        for toolname, tool in self.tools.items():
            tool.resolve_extra_files()
            if len(tool.wanted_files) == 0:
                logger.info(f"tool %s is non-fst (no requirements on GTLANGS-specific files)", toolname)

            tool.pipelines = resolve_pipelines(tool.pipelines, available_files)
            tool.langs = list(tool.pipelines.keys())
            for lang in tool.langs:
                self.capabilities[lang].append(toolname)

            for lang in self.capabilities:
                tool.on_startup(lang)

    def print_available_tools_by_language(self):
        """Prints a list of languages, and which tools are available for each of those."""
        for lang, tools in self.capabilities.items():
            print(f"Available tools for language '{lang}': {', '.join(tools)}")

    def print_available_langs_by_tool(self):
        """Prints a list of tools, and which languages are available for each of those."""
        pass


tools = Tools()

from . import toolspecs
for name, spec in inspect.getmembers(toolspecs):
    if not name.startswith("__"):
        tools.add(spec)

tools.resolve_pipelines()
tools.print_available_tools_by_language()

