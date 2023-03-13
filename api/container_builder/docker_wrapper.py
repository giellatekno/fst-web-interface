import asyncio
import sys
from functools import partial
from itertools import count
from subprocess import PIPE
from multiprocessing import cpu_count
from os import get_terminal_size

builtin_print = __builtins__["print"]
COLUMNS = get_terminal_size().columns


async def _write(fd, data):
    fd.write(data)
    await fd.drain()
    fd.close()


async def _read(fd):
    return await fd.readline()


async def run_docker_build(image_tag, input, verbose=False, print=print):
    """Run the Dockerfile given in 'input', and tag it as 'image_tag'."""
    assert isinstance(input, str), "input must be string"
    input = input.strip().encode("utf-8")

    proc = await asyncio.create_subprocess_shell(
            f"docker build -t {image_tag} -",
            limit=4096, stdin=PIPE, stdout=PIPE)

    # prevent deadlock
    # see https://stackoverflow.com/questions/57730010/python-asyncio-subprocess-write-stdin-and-read-stdout-stderr-continuously
    _, line1 = await asyncio.gather(
        _write(proc.stdin, input),
        _read(proc.stdout)
    )

    lookfor = bytes(f"Successfully tagged {image_tag}", encoding="utf-8")

    if line1.startswith(lookfor):
        print("done")
        return True

    print(line1.decode("utf-8"))

    while True:
        line = await proc.stdout.readline()
        if line.startswith(lookfor):
            print("done")
            return image_tag
        elif line == b"":
            print("Error: unexpected EOF")
            return False
        else:
            print(line.decode("utf-8").strip())


async def worker(q, r, verbose=False):
    """A worker, taking work items from a queue 'q', until there are no more
    items left on the queue to take. Work item is a 3-tuple of
    (id, function, print_function). The worker calls the async function
    'function', with keyword argument 'print' = print_function, and puts
    the result of the call back on a return queue 'r' as (id, result)."""
    while True:
        try:
            idx, f, print_fn = q.get_nowait()
        except asyncio.QueueEmpty:
            break

        f, *args = f

        res = await f(*args, verbose=verbose, print=print_fn)

        r.put_nowait([idx, res])
        q.task_done()


async def run_assignments(*assignments, verbose=False):
    """Run multiple assignments in parallel using asyncio.gather()"""
    n = len(assignments)
    names, funcs = zip(*assignments)

    if verbose:
        print_fns = [print for _ in range(n)]
    else:
        print_fns = [
            partial(logit, i, name)
            for i, name in zip(range(n, 0, -1), names)
        ]

    q = asyncio.Queue()
    for idx, fn, print_fn in zip(count(), funcs, print_fns):
        q.put_nowait([idx, fn, print_fn])

    for name in names:
        print(name + "...(waiting)")

    r = asyncio.Queue()
    workers = [
        asyncio.create_task(worker(q, r, verbose))
        for _ in range(cpu_count())
    ]

    try:
        await asyncio.gather(*workers)
    except asyncio.CancelledError as e:
        print("cancelled.", e)

    results = [None for _ in range(n)]
    while True:
        try:
            res = r.get_nowait()
        except asyncio.QueueEmpty:
            break

        idx, result = res
        results[idx] = result

    return results if len(results) > 1 else results[0]


def logit(n, title, s):
    """Go n lines back, erase the line, print a string, and go back
    down again"""
    s = s.strip()
    if s.startswith("--->"):
        return
    avail = COLUMNS - len(title)
    if len(s) > avail:
        s = s[:avail - 3] + "..."
    builtin_print(f"\x1b[{n}F\x1b[K", end="")
    builtin_print(f"{title}...{s}", end="")
    builtin_print(f"\x1b[{n}E", end="")
    sys.stdout.flush()


