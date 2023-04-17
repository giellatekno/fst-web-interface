import asyncio
import builtins
import os
import sys
from random import random
from unittest import mock
from contextlib import ExitStack

builtin_print = builtins.print


def move_up(n): builtin_print(f"\x1b[{n}F", end="")
def move_down(n): builtin_print(f"\x1b[{n}E", end="")
def clear_line(): builtin_print("\r\x1b[K", end="")


def fit_to_terminal(line):
    terminal_width = os.get_terminal_size().columns
    if len(line) > terminal_width:
        line = line[0:terminal_width - 3] + "..."
    return line


def print_on_line(n, s):
    move_up(n)
    clear_line()
    builtin_print(s, flush=True, end="")
    move_down(n)


def find_job_by_task(jobs, task):
    for job, t in jobs.items():
        if t is task:
            return job
    assert False, "Unheld invariant: find_job_by_task(): task was not found"


class Job:
    """ A job to be run. """

    def __init__(self, id, title, coro):
        self.id = id
        self.title = title
        self.coro = coro
        self.status = "initial"
        self.exception = None
        self.result = None

    def __str__(self):
        if self.exception is not None:
            s = f'exception={str(type(self.exception))}'
        else:
            s = f'result={self.result}'

        return (
            "Job { "
            f"id={self.id}, "
            f"index={self.index}, "
            f'title="{self.title}", '
            f'status="{self.status}", '
            f"{s}"
            "}"
        )

    def __repr__(self):
        return str(self)


class Jobs:
    def __init__(self, jobs, workers):
        # type: dict[job, asyncio.Task]
        self._jobs = jobs
        self.queue = asyncio.Queue()
        self.running_jobs = {}
        self.done_jobs = []
        self.workers = workers

        for i, job in enumerate(jobs):
            print(f"{job.title}: (waiting to start)")
            job.index = i
            self.queue.put_nowait(job)

    @property
    def n(self):
        return len(self._jobs)

    def assign_jobs_to_workers(self):
        """Pull jobs from the job queue one by one, and assign them to an
        available worker. Stops when there are no more jobs in the job queue,
        or there are no more available workers."""
        while len(self.running_jobs) < self.workers and not self.queue.empty():
            job = self.queue.get_nowait()
            job.status = "running"
            task = asyncio.create_task(job.coro())
            self.running_jobs[job] = task

    def find_job_by_task(self, task):
        for job, t in self.running_jobs.items():
            if t is task:
                return job
        assert False, "Unheld invariant: find_job_by_task(): task not found"

    def handle_done_tasks(self, done):
        """Iterate the lists of done and pending, and update the job's status,
        and modify running_jobs and done_jobs accordingly. Returns True if any
        of the tasks failed with an exception, False if not."""
        failed = False
        cancelled = False

        n = 0
        for done_task in done:
            n += 1
            job = self.find_job_by_task(done_task)
            del self.running_jobs[job]
            self.done_jobs.append(job)

            if done_task.cancelled():
                print_on_line(self.n - job.index, f"{job.title}: (cancelled)")
                if job.status != "aborted":
                    job.status = "cancelled"
            else:
                exc = done_task.exception()
                if exc is not None:
                    print_on_line(self.n - job.index, f"{job.title}: (failed)")
                    job.status = "failed"
                    job.exception = exc
                    failed = True
                else:
                    print_on_line(self.n - job.index, f"{job.title}: (done)")
                    job.status = "done"
                    job.result = done_task.result()

        return failed, cancelled

    def drain_job_queue(self, new_status):
        while not self.queue.empty():
            job = self.queue.get_nowait()
            job.status = new_status
            print_on_line(self.n - job.index, f"{job.title}: ({new_status})")
            self.done_jobs.append(job)

    async def run_all(
        self,
        abort_on_first_failed=False,
        fancy_printer=True,
    ):
        running = True

        with ExitStack() as stack:
            if fancy_printer:
                print_fn = make_printer(self.running_jobs, self.n, False)
                stack.enter_context(
                    mock.patch("builtins.print", print_fn)
                )

            while running:
                self.assign_jobs_to_workers()

                if not self.running_jobs:
                    break

                try:
                    done, pending = await asyncio.wait(
                        self.running_jobs.values(),
                        return_when=asyncio.FIRST_COMPLETED
                    )
                except asyncio.CancelledError:
                    # cancel all tasks, and go again from the top.
                    # the next time around, they will all be in 'done',
                    # with a status of "cancelled"
                    for job, task in self.running_jobs.items():
                        if not task.done():
                            task.cancel()
                    self.drain_job_queue("cancelled")
                else:
                    failed, cancelled = self.handle_done_tasks(done)
                    if failed and abort_on_first_failed:
                        self.drain_job_queue("aborted")

                        # request the tasks to be cancelled
                        for job, task in self.running_jobs.items():
                            job.status = "aborted"
                            if not task.done():
                                task.cancel()

                    if cancelled:
                        running = False

        assert len(self.running_jobs) == 0, "running_jobs should be empty"

        return self.done_jobs


def make_printer(tasks, n_total_jobs, verbose=False):
    def our_print(*args, sep=" ", end="\n", file=None, flush=False):
        # If printing to something else than stdout, then just print
        # with the builtin print
        if file is not None and file is not sys.stdout:
            builtin_print(*args, sep, end, flush=flush, file=file)

        job = find_job_by_task(tasks, asyncio.current_task())
        index = job.index
        title = job.title

        s = (sep.join(map(str, args)) + end).strip()
        line = fit_to_terminal(f"{title}: {s}")
        if verbose:
            builtin_print(line)
        else:
            print_on_line(n_total_jobs - index, line)

    return our_print


async def run_jobs(
    jobs,
    workers=4,
    scrollback=3,
    abort_on_first_failed=False,
    cpu_bound=None,
    fancy_printer=True,
):
    if cpu_bound is True:
        # cpu_bound explicitly set to True, limit number of workers to
        # how many cpus we have available
        workers = len(os.sched_getaffinity(0))
    elif cpu_bound is False:
        # cpu bound explicitly set to False, so run all jobs in parallell
        workers = len(jobs)

    if workers > len(jobs):
        workers = len(jobs)

    _jobs = Jobs(jobs, workers)

    return await _jobs.run_all(
        abort_on_first_failed=abort_on_first_failed,
        fancy_printer=fancy_printer
    )


def mk_fn(i, fails=False):
    async def inner():
        msgs = [f"{i}-{j}" for j in range(6)]
        for msg in msgs:
            print(msg)
            await asyncio.sleep(0.1 + random() / 3)

        if fails:
            raise Exception()
        else:
            print(f"{i}-done")
            return i

    return inner


async def fails():
    raise Exception()


async def main():
    jobs = Jobs([
        Job(id=1, title="tittel 1", coro=mk_fn(1)),
        Job(id=2, title="tittel 2", coro=mk_fn(2, fails=True)),
        Job(id=3, title="tittel 3", coro=mk_fn(3)),
        Job(id=4, title="tittel 4", coro=mk_fn(4)),
        Job(id=5, title="tittel 5", coro=mk_fn(5)),
    ], workers=2)

    done_list = await jobs.run_all(abort_on_first_failed=True)
    print(done_list)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
