import contextlib
import logging
import multiprocessing
import typing
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from threading import RLock as TRLock


class DummyLock:
    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass


TRLOCK = TRLock()
PRLOCK = DummyLock()


logger = logging.getLogger(__name__)


def _init_process(lock):
    global PRLOCK
    PRLOCK = lock


@contextlib.contextmanager
def executor(kind: str, max_workers: int) -> typing.Iterator[Executor]:
    """General purpose utility to get an executor with its as_completed handler

    This allows us to easily use other executors as needed.
    """
    global PRLOCK

    if kind == "thread":
        with ThreadPoolExecutor(max_workers=max_workers) as pool_t:
            yield pool_t
    elif kind == "process":
        m = multiprocessing.Manager()
        lock = m.RLock()
        with ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=_init_process,
            initargs=(lock,),
        ) as pool_p:
            yield pool_p
        PRLOCK = DummyLock()
    else:
        raise NotImplementedError("That kind is not implemented")
