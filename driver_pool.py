from __future__ import annotations
from typing import Callable, Optional, TypeVar
from threading import Lock, Event
import queue

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

T = TypeVar("T")

class FirefoxWebDriverPool:
    def __init__(self, max_drivers: int, headless: bool = True):
        self._available_drivers = queue.Queue(maxsize=max_drivers)
        self._terminating = False
        self._can_terminate = Event()

        self._pending_lock = Lock()  # TODO: Find a clean way of using Queue.qsize instead
        self._n_pending = 0

        options = Options()
        options.headless = headless

        for _ in range(max_drivers):
            self._available_drivers.put(Firefox(options=options))

    def run_job(self, job: Callable[[Firefox], T]) -> Optional[T]:
        """Runs a job in a browser pool.
        Will return the result of the job if the job succeeded, or None if the job failed
        due to termination of the pool being in progress."""
        driver = None
        try:
            with self._pending_lock:
                if self._terminating:
                    return None
                else:
                    self._n_pending += 1
                    self._can_terminate.clear()

            driver = self._available_drivers.get()
            return job(driver)
        finally:
            # Should never be None, but could theoretically be if a lock throws due to a bug in our logic.
            if driver is not None:
                self._available_drivers.put(driver)  # Should not be possible to be full.
            with self._pending_lock:
                self._n_pending -= 1
                if self._n_pending == 0:
                    self._can_terminate.set()

    def terminate(self) -> None:
        self._terminating = True
        self._can_terminate.wait()

        while self._available_drivers.qsize() > 0:
            driver: Firefox = self._available_drivers.get()
            driver.quit()

    def __enter__(self) -> FirefoxWebDriverPool:
        return self

    def __exit__(self, *_) -> None:
        self.terminate()
