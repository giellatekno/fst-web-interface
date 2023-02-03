import asyncio
import inspect
import logging
import shlex
import subprocess
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from .config import GTLANGS
from .util import PartialPath
from .util import noop

# this imports all toolspecs as a module with the name "toolspecs"
from . import toolspecs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

DETECTED_GTLANGS = list(p.name[5:] for p in GTLANGS.glob("lang-*"))


def get_repo_info(path):
    prog = shlex.split("git log -n 1 --format=format:\"%h %cI\"")
    res = subprocess.run(prog, capture_output=True, text=True,
                         env={"GIT_DIR": f"{path}/.git"})
    if not res.stdout:
        return None

    hash, date = res.stdout.strip().split(" ", maxsplit=1)
    return {"hash": hash, "date": date}


def flat(some_list):
    out = []
    for sublist in some_list:
        out.extend(sublist)
    return out


class Tool:
    """Each file in toolspecs/ is a "Tool", and it is handled by this class."""

    def __init__(self, spec):
        self.spec = spec
        self.name = spec.__name__.split(".")[-1]
        spec_dict = dict(inspect.getmembers(spec))
        self.description = spec_dict.get("description", "(no description)")
        self.summary = spec_dict.get("summary", "(no summary given)")
        self.pipelines = spec_dict["pipeline"]
        self.normalize_pipelines()
        self.resolve_pipelines()
        self.query_params = spec_dict.get("query_params", {})
        self.extra_files = spec_dict.get("extra_files", {})
        self.find_response_model()

        if "on_startup" not in spec_dict:
            self.on_startup = noop
        else:
            on_startup = spec_dict["on_startup"]
            if not callable(on_startup):
                msg = f"toolspec/{self.name}: on_startup must be a function"
                logger.error(msg)
                on_startup = noop
            self.on_startup = on_startup

    def normalize_pipelines(self):
        """Make sure `pipelines` is a dictionary of lang -> pipeline"""
        if isinstance(self.pipelines, list):
            default_pipeline = self.pipelines
            self.pipelines = {}
        else:
            default_pipeline = self.pipelines["*"]
            # TODO what if no default pipeline?

        for available in DETECTED_GTLANGS:
            if available not in self.pipelines:
                self.pipelines[available] = deepcopy(default_pipeline)

        if "*" in self.pipelines:
            del self.pipelines["*"]

    def resolve_pipelines(self):
        """Resolve the PartilPaths given in all pipelines to real Paths,
        and log a warning for when files are not found"""
        new_pipelines = {}
        self.langs = []

        for lang, pipeline in self.pipelines.items():
            assert lang != "*", "\"*\" still exists"
            new_pipeline = []

            for program in pipeline:
                if not isinstance(program, list):
                    # program is a python function
                    new_pipeline.append(program)
                    continue

                new_program = []
                for entry in program:
                    if not isinstance(entry, PartialPath):
                        new_program.append(entry)
                        continue

                    pp = entry.p
                    resolved_path = GTLANGS / f"lang-{lang}" / pp
                    if resolved_path.is_file():
                        new_program.append(str(resolved_path))
                    else:
                        logger.warn(f"lang-{lang} wants file {pp}, but"
                                    f" {resolved_path} does not exist")
                        new_program = None
                        break
                if new_program is not None:
                    new_pipeline.append(new_program)
                else:
                    new_pipeline = None
                    break

            if new_pipeline is not None:
                new_pipelines[lang] = new_pipeline
                self.langs.append(lang)

        self.pipelines = new_pipelines

    def find_response_model(self):
        """Find the response model of *all* pipelines. All pipelines must have
        the same response model, because each tool is one route in fastapi,
        and one route can only have one response model. Maybe it would be
        possible to make some kind of combination of all response models,
        that's not really needed."""
        if not self.pipelines:
            self.response_model = None

        last_step = next(iter(self.pipelines.values()))[-1]

        if isinstance(last_step, list):
            self.response_model = str
        elif callable(last_step):
            ret_ann = inspect.signature(last_step).return_annotation
            if ret_ann is inspect.Signature.empty:
                self.response_model = Any
            else:
                self.response_model = ret_ann

    def resolve_extra_files(self):
        """Gets called once per tool"""
        # if not self.extra_files:
        #     this tool doesn't have any extra files, just skip out immediately
        #     return []
        available_langs = []

        for p in GTLANGS.glob("lang-*"):
            lang = p.name[5:]

            if lang not in self.extra_files:
                self.extra_files[lang] = {}

            if "*" in self.extra_files:
                star_updates = {}
                for entry, partial_path in self.extra_files["*"].items():
                    file_path = p / partial_path.p
                    if file_path.is_file():
                        star_updates[entry] = file_path
                    else:
                        logger.warn(f"lang-{lang} wants file {partial_path.p}, but it was not found")
                        star_updates[entry] = None

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
                        updates[entry] = None
                        #logger.warn(f"lang-{lang} wants file {partial_path.p}, but it was not found")
                self.extra_files[lang].update(updates)

            if any(value is None for value in self.extra_files[lang].values()):
                logger.error(f"tool:{self.name} for lang={lang} disabled due to missing files")
            else:
                available_langs.append(lang)

        return available_langs

    async def _run_callable(self, fn, input, lang, query_params=None):
        is_coroutine = inspect.iscoroutinefunction(fn)
        takes_query_params = "query_params" in inspect.signature(fn).parameters

        match (is_coroutine, takes_query_params):
            case (True, True):
                output = await fn(input, str(lang), query_params=query_params)
            case (True, False):
                output = await fn(input)
            case (False, True):
                output = fn(input, str(lang), query_params=query_params)
            case (False, False):
                output = fn(input)

        return output

    async def run_pipeline(self, lang, input, query_params=None):
        final_output = {"input": input}
        pipeline = self.pipelines[lang]

        for prog in pipeline:
            if callable(prog):
                try:
                    step_output = await self._run_callable(
                            prog, input, lang, query_params)
                except Exception as e:
                    msg = f"Python step in pipeline threw unhandled exception: {e}"
                    logger.exception(msg)
                    final_output["error"] = msg
                    return final_output

                input = step_output
            else:
                all_ok = all(isinstance(x, (str, Path)) for x in prog)
                assert all_ok, prog
                PIPE = subprocess.PIPE
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
        self.tools: dict[str, Tool] = {}
        self.repo_info_for_lang: dict[str, dict] = {}
        self.tools_for_lang = defaultdict(list)

    def add(self, spec):
        tool = Tool(spec)
        self.tools[tool.name] = tool
        for lang in tool.langs:
            self.tools_for_lang[lang].append(tool.name)

        return tool

    def capabilities(self):
        out = {}

        for lang, tools in self.tools_for_lang.items():
            out[lang] = {
                "tools": tools,
                "repo_info": self.repo_info_for_lang[lang]
            }

        return out

    def collect_repos_info(self):
        for p in GTLANGS.glob("lang-*"):
            lang = p.name[5:]
            if repo_info := get_repo_info(p):
                self.repo_info_for_lang[lang] = repo_info


tools = Tools()

for name, spec in inspect.getmembers(toolspecs):
    if not name.startswith("__"):
        tools.add(spec)

tools.collect_repos_info()
