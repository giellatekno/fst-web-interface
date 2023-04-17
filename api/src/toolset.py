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
from .util import noop
from .langmodel_file import LangmodelFile

# this imports all toolspecs as a module with the name "toolspecs"
from . import toolspecs

logger = logging.getLogger(__name__)
if __name__ == "__main__":
    # if run as a script, disable logging
    logging.disable(logging.ERROR)
else:
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


def find_gt_file(GTLANGS, lang, langmodel_file):
    """Given the GTLANGS path, a language code, and a PartialPath,
    return the path of where the file specified by the partialpath
    was found, or, if it was not found, return None."""
    # so, check GTLANGS, but also /usr/share/giella/{lang}
    # also check /usr/share/giella/{lang} ?
    for base in (GTLANGS, Path("/usr/share/giella")):
        for lang_part in (f"lang-{lang}", lang):
            path = langmodel_file.resolve_path(base / lang_part)
            if path.is_file():
                return path


class Tool:
    """Each file in toolspecs/ is a "Tool", and it is handled by this class."""

    def __init__(self, spec):
        self.spec = spec
        self.name = spec.__name__.split(".")[-1]

        # which languages are available for this tool
        self.langs = set()

        spec_dict = dict(inspect.getmembers(spec))
        self.description = spec_dict.get("description", "(no description)")
        self.summary = spec_dict.get("summary", "(no summary given)")
        self.query_params = spec_dict.get("query_params", {})
        self.extra_files = spec_dict.get("extra_files", {})
        self.pipelines = spec_dict["pipeline"]
        self.needed_gt_files = {}
        self.resolve_pipelines()

        # this technically returns available files
        # TODO but where is it define that this tool should work for
        # language X ? currently in docs paradigm tool is only
        # available for nob and smj... (??)
        self.resolve_extra_files()

        self.find_response_model()
        self.langs = list(self.langs)

        self.on_startup = spec_dict.get("on_startup", noop)
        if not callable(self.on_startup):
            msg = f"toolspec/{self.name}: on_startup must be a function"
            logger.error(msg)
            self.on_startup = noop

        for lang in DETECTED_GTLANGS:
            if lang in self.langs:
                self.on_startup(lang, self.extra_files)
            else:
                pass  # print(f"skipping on_startup for ({self.name}, {lang})")

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
        self.normalize_pipelines()

        new_pipelines = {}
        disabled_langs = defaultdict(set)

        for lang, pipeline in self.pipelines.items():
            assert lang != "*", "\"*\" still exists in pipeline"
            self.needed_gt_files[lang] = set()
            new_pipeline = []

            for program in pipeline:
                if not isinstance(program, list):
                    # program is a python function
                    new_pipeline.append(program)
                    continue

                new_program = []
                for entry in program:
                    if not isinstance(entry, LangmodelFile):
                        new_program.append(entry)
                        continue

                    self.needed_gt_files[lang].add(entry.name)
                    found_path = find_gt_file(GTLANGS, lang, entry)
                    if found_path:
                        new_program.append(str(found_path))
                    else:
                        disabled_langs[lang].add(entry.name)
                        new_program = None
                        break
                if new_program is not None:
                    new_pipeline.append(new_program)
                else:
                    new_pipeline = None
                    break

            if new_pipeline is not None:
                new_pipelines[lang] = new_pipeline
                self.langs.add(lang)

        for lang, files in disabled_langs.items():
            logger.error(
                f"({self.name}, {lang}) disabled due to missing pipeline"
                f' files: {", ".join(files)}'
            )

        self.pipelines = new_pipelines

    def find_response_model(self):
        """Find the response model of *all* pipelines. All pipelines must have
        the same response model, because each tool is one route in fastapi,
        and one route can only have one response model. Maybe it would be
        possible to make some kind of combination of all response models,
        that's not really needed."""
        if not self.pipelines:
            self.response_model = None
            return

        last_step = next(iter(self.pipelines.values()))[-1]

        if isinstance(last_step, list):
            self.response_model = str
        elif callable(last_step):
            ret_ann = inspect.signature(last_step).return_annotation
            if ret_ann is inspect.Signature.empty:
                self.response_model = Any
            else:
                self.response_model = ret_ann

    def normalize_extra_files(self):
        """Make sure `self.extra_files` is a dict of lang -> extra files."""
        if not isinstance(self.extra_files, dict):
            msg = "'extra_files' must be a dict"
            logger.critical(msg)
            exit()

        default_extra_files = self.extra_files.get("*")

        if default_extra_files:
            for lang in DETECTED_GTLANGS:
                if lang not in self.extra_files:
                    self.extra_files[lang] = deepcopy(default_extra_files)
                else:
                    self.extra_files[lang].update(**deepcopy(default_extra_files))

        if default_extra_files:
            del self.extra_files["*"]

    def resolve_extra_files(self):
        """Gets called once per tool"""
        self.normalize_extra_files()

        if not self.extra_files:
            # this tool doesn't have any extra files, just skip out immediately
            return

        disabled_langs = defaultdict(set)

        for p in GTLANGS.glob("lang-*"):
            lang = p.name[5:]

            if lang not in self.extra_files:
                continue

            updated = {}
            for entry, path in self.extra_files[lang].items():
                if isinstance(path, LangmodelFile):
                    path = path.resolve_path(p, lang)

                if path.is_file():
                    updated[entry] = path
                else:
                    disabled_langs[lang].add(str(path))
                    updated[entry] = None

            self.extra_files[lang] = updated

            if all(value is not None for value in self.extra_files[lang].values()):
                self.langs.add(lang)

        for lang, files in disabled_langs.items():
            logger.warn(
                f"({self.name}, {lang}) disabled due to missing extra files "
                f" {', '.join(files)}"
            )

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

if __name__ == "__main__":
    # dict of lang -> set of file paths
    # needed = {lang: set() for lang in LANGS}
    import json

    class MyEncoder(json.JSONEncoder):
        def default(self, o):
            """ For sets: return a list, which can be serialized. """
            if isinstance(o, set):
                return list(o)
            return super().default(o)

    got = defaultdict(set)
    for name, tool in tools.tools.items():
        for lang, needed_files in tool.needed_gt_files.items():
            got[lang] |= needed_files

    print(json.dumps(got, indent=4, cls=MyEncoder))
