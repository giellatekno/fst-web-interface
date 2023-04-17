import asyncio
# import sys
import json
import re
# from functools import partial
# from itertools import count
from subprocess import PIPE
from string import ascii_letters
from random import choices
from pathlib import Path
from io import StringIO
# from multiprocessing import cpu_count
# from os import get_terminal_size

builtin_print = __builtins__["print"]
# COLUMNS = get_terminal_size().columns


def random_name():
    return "".join(choices(ascii_letters, k=8))


async def _write(fd, data):
    fd.write(data)
    await fd.drain()
    fd.close()


async def _read(fd):
    return await fd.readline()


async def docker_list_images(name):
    proc = await asyncio.create_subprocess_shell(
        f"docker image list {name} --format json",
        stdout=PIPE
    )
    stdout, _stderr = await proc.communicate()

    return [json.loads(line) for line in stdout.decode("utf-8").splitlines()]


async def docker_create(image, name=None):
    name = f"--name {name}" if name is not None else ""

    proc = await asyncio.create_subprocess_shell(
        f"docker create {name} {image}",
    )
    retcode = await proc.wait()
    if retcode != 0:
        raise Exception("docker_create(): unable to make container from image")


async def docker_rm_container(name):
    proc = await asyncio.create_subprocess_shell(
        f"docker rm {name}",
    )
    retcode = await proc.wait()
    return retcode


async def docker_cp(container, container_path, dest_path):
    proc = await asyncio.create_subprocess_shell(
        f"docker cp {container}:{container_path} {dest_path}"
    )
    retcode = await proc.wait()
    return retcode


async def docker_cp_from_image(image, source, destination):
    p = Path(destination).resolve()
    p.mkdir(parents=True, exist_ok=True)
    temp_container_name = "temp-" + random_name()
    await docker_create(image, name=temp_container_name)
    await docker_cp(temp_container_name, source, destination)
    await docker_rm_container(temp_container_name)


async def docker_run(image, cmd):
    proc = await asyncio.create_subprocess_shell(
        f"docker run --rm -t {image} {cmd}",
        stdout=PIPE, stderr=PIPE, limit=4096
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode("utf-8"), stderr.decode("utf-8")


async def docker_image_rm(name):
    proc = await asyncio.create_subprocess_shell(
        f"docker image rm {name}",
        stdout=PIPE
    )
    await proc.communicate()


def is_done_line(line):
    if "naming to" in line:
        return True
    return False
    m = re.match(r"#\d+ DONE", line)
    if m:
        return True
    return False


def is_error_line(line):
    if line.startswith("ERROR"):
        return True
    m = re.match(r"#\d+ ERROR", line)
    if m:
        return True
    return False


async def docker_build(dockerfile, tag=None, build_context=None, disable_cache=False):
    """Run `docker build` with the Dockerfile given in the string `dockerfile`,
    and, if tag is a string, tag the image with `tag`.
    Returns a 2-tuple of (ok, tag)."""
    assert isinstance(dockerfile, str), "dockerfile must be string"
    dockerfile = dockerfile.strip().encode("utf-8")

    cmd = "docker build"
    if isinstance(build_context, dict) and len(build_context) > 0:
        cmd += " --build-context "
        cmd += ",".join(f"{k}={v}" for k, v in build_context.items())

    if isinstance(tag, str):
        cmd += f" -t {tag}"
    if disable_cache:
        cmd += " --no-cache"
    cmd += " -"

    proc = await asyncio.create_subprocess_shell(
            cmd, limit=4096, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    log = StringIO()

    # prevent deadlock
    # see https://stackoverflow.com/questions/57730010/python-asyncio-subprocess-write-stdin-and-read-stdout-stderr-continuously
    async with asyncio.TaskGroup() as tg:
        tg.create_task(_write(proc.stdin, dockerfile))
        tg.create_task(_read(proc.stderr))

    while True:
        line = (await proc.stderr.readline()).strip().decode("utf-8")
        log.write(line + "\n")
        if is_done_line(line):
            return
        elif is_error_line(line):
            print(line)
            raise Exception(log)
        else:
            print(line)


# async def worker(q, r, verbose=False):
#     """A worker, taking work items from a queue 'q', until there are no more
#     items left on the queue to take. Work item is a 3-tuple of
#     (id, function, print_function). The worker calls the async function
#     'function', with keyword argument 'print' = print_function, and puts
#     the result of the call back on a return queue 'r' as (id, result)."""
#     while not q.empty():
#         id, fn, print_fn = q.get_nowait()
# 
#         try:
#             result = await fn(verbose=verbose, print=print_fn)
#         except asyncio.CancelledError:
#             print_fn("skipped due to ctrl-c by user")
#         else:
#             r.put_nowait([id, result])
#             q.task_done()
# 
# 
# async def run_assignments(
#     assignments,
#     verbose=False,
#     interpret_result=lambda result: bool(result),
# ):
#     """Run multiple assignments in parallel using asyncio.TaskGroup.
#     An "assignment" is a tuple of (name, function), where the name
#     is a string, and function is a tuple where the first element is
#     the function to call, and the rest are the parameters."""
# 
#     n = len(assignments)
#     identifiers, titles, funcs = zip(*assignments)
# 
#     aborted = set(identifiers)
#     succeeded = {}
#     failed = {}
# 
#     if verbose:
#         print_fns = [print for _ in range(n)]
#     else:
#         print_fns = [
#             partial(logit, i, title)
#             for i, title in zip(range(n, 0, -1), titles)
#         ]
# 
#     q = asyncio.Queue()
#     for id, fn, print_fn in zip(identifiers, funcs, print_fns):
#         q.put_nowait([id, fn, print_fn])
# 
#     for title in titles:
#         print(f"{title}...(waiting to start)")
# 
#     r = asyncio.Queue()
#     try:
#         async with asyncio.TaskGroup() as tg:
#             for _ in range(cpu_count()):
#                 tg.create_task(worker(q, r, verbose))
#     except asyncio.exceptions.CancelledError:
#         print("Step aborted early by ctrl-c")
# 
#     while not r.empty():
#         identifier, result = r.get_nowait()
#         aborted.remove(identifier)
# 
#         succeess = interpret_result(result)
#         if succeess:
#             succeeded[identifier] = result
#         else:
#             failed[identifier] = result
# 
#     return succeeded, failed, aborted
# 
# 
# def logit(n, title, s):
#     """Go n lines back, erase the line, print a string, and go back
#     down again"""
#     s = s.strip()
#     avail = COLUMNS - len(title) - 3
#     if len(s) > avail:
#         s = s[:avail - 6] + "..."
#     builtin_print(f"\x1b[{n}F\x1b[K", end="")
#     builtin_print(f"{title}...{s}", end="")
#     builtin_print(f"\x1b[{n}E", end="")
#     sys.stdout.flush()
