from AutoComplete import *
import threading
from typing import List, Callable


class MainLoop:
    TIMER_NAME = "alive"
    threads: List[threading.Thread] = []

    @classmethod
    def is_alive(cls) -> bool:
        return Timer.Remaining(cls.TIMER_NAME) > 0

    @classmethod
    def start(cls, delay: int = 100, lifetime: int = 1000):
        Timer.Create(cls.TIMER_NAME, lifetime)
        for thread in cls.threads:
            if not thread.is_alive():
                thread.start()
        while True:
            Timer.Create(cls.TIMER_NAME, lifetime)
            Misc.Pause(delay)

    @classmethod
    def add_thread(cls, target: Callable):
        worker_thread = threading.Thread(target=target, args=(cls,))
        worker_thread.daemon = True
        cls.threads.append(worker_thread)
        return worker_thread


@MainLoop.add_thread
def background_worker(loop):
    count = 0
    while loop.is_alive():
        count += 1
        Misc.SendMessage(f"Running on background... ({count} second)")
        Misc.Pause(1000)
    Misc.SendMessage("Process halted.")


MainLoop.start()
