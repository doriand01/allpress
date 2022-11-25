import concurrent.futures
import threading
import requests

from allpress.settings import logging

logging.getLogger(__name__)

from time import sleep

class States:
    LOW = 0
    LIGHT = 1
    REGULAR = 2
    MODERATE = 3
    HEAVY = 4

class HTTPRequestPoolManager:



    def __init__(self,  max_concurrent_requests=256):
        self.load_state = States.LOW
        self.max_concurrent_requests = max_concurrent_requests
        self.n_active_concurrent_requests = 0
        self._request_pool = []
        self._pool_futures = []
        self._pool_manager_active = False
        logging.info('New HTTPRequestPoolManager instatiated.')

    
    """
    Returns the load of the RequestPoolManager as a State value.
    Calculated from the maximum number of allowed concurrent requests
    `self.max_concurrent_requests` divided by the total number of
    active concurrent requests.
    """
    def _get_state(self):
        if self._get_load() < 20.0:
            return States.LOW
        elif 20.0 < self._get_load() < 33.3:
            return States.LIGHT
        elif 33.3 < self._get_load() < 50.0:
            return States.REGULAR
        elif 50.0 < self._get_load() <  75.0:
            return States.MODERATE
        elif self._get_load() > 75.0:
            return States.HEAVY


    def _get_load(self) -> float:
        return self.max_concurrent_requests / self.n_active_concurrent_requests


    def _execute_request(self, url: str) -> requests.models.Response:
        return requests.get(url)


    def _execute_pool(self):
        pool_executor = concurrent.futures.ThreadPoolExecutor()
        while self._pool_manager_active:
            if len(self._request_pool) > 0:
                for request_url in self._request_pool:
                    if self._get_state() <= 1:
                        self.n_active_concurrent_requests += 1
                        self._request_pool.remove(request_url)
                        self._pool_futures.append(pool_executor.submit(self._execute_request, request_url))
                    if self._get_state() == 2:
                        sleep(0.01)
                        self.n_active_concurrent_requests += 1
                        self._request_pool.remove(request_url)
                        self._pool_futures.append(pool_executor.submit(self._execute_request, request_url))
                    if self._get_state() == 3:
                        logging.info('Moderate request load. Rate limiting by sleeping for 0.25 seconds.')
                        sleep(0.25)
                        self.n_active_concurrent_requests += 1
                        self._request_pool.remove(request_url)
                        self._pool_futures.append(pool_executor.submit(self._execute_request, request_url))
                    if self._get_state() == 4:
                        logging.warning('Heavy load. Throttling by half a second.')
                        sleep(0.5)
                        self.n_active_concurrent_requests += 1
                        self._request_pool.remove(request_url)
                        self._pool_futures.append(pool_executor.submit(self._execute_request, request_url))
            elif len(self._request_pool) == 0:
                self._pool_manager_active = False

    def execute_request_batch(self, batch: list) -> list:
        logging.info(f'Executing request batch of {len(batch)} requests.')
        self.n_active_concurrent_requests += len(batch)
        self._request_pool = self._request_pool + batch
        self._pool_manager_active = True
        logging.info('Starting batch thread.')
        thread = threading.Thread(target=self._execute_pool)
        thread.start()
        thread.join()
        while not thread.is_alive():
            self.n_active_concurrent_requests = 0
            return concurrent.futures.as_completed(self._pool_futures)




    