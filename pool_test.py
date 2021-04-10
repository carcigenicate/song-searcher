from typing import List

import driver_pool
from multiprocessing.pool import ThreadPool

def d_job(driver: driver_pool.Firefox) -> List[str]:
    driver.get("http://192.168.50.48")
    links = driver.find_elements_by_tag_name("a")
    return [l.text for l in links]


def test():
    with driver_pool.FirefoxWebDriverPool(2, False) as d_pool, \
         ThreadPool(100) as thread_pool:

        print("Pools Created")

        results = thread_pool.map(lambda _: d_pool.run_job(d_job), range(100))

        print("N Results: ", len(results))

        for r in results:
            print(r)

        print("Running bad job...")
        thread_pool.apply(lambda: d_pool.run_job(lambda d: d.get("some_invalid-crap  BAD")))

        thread_pool.close()