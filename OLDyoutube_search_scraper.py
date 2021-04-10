from __future__ import annotations
from typing import List, Tuple
from urllib.parse import quote_plus


from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


WAIT_TIMEOUT = 3
SEARCH_BASE_URL = "https://www.youtube.com/results?search_query="
# A "fingerprint" of classes that uniquely identifies result elements from other elements on the page
SIMPLE_SEARCH_RESULT_CLASS_FINGERPRINT = "text-wrapper.style-scope.ytd-video-renderer"

# Occasionally, the search results are returned in a different, non-list style with a different fingerprint.
FALLBACK_SEARCH_RESULT_CLASS_FINGERPRINT = "yt-simple-endpoint.style-scope.ytd-rich-grid-media"


def get_top_search_results(driver: WebDriver, search_term: bytes) -> List[Tuple[str, str]]:
    """Returns a list of tuples of (Video Title, URL) pairs.
    Only returns search results that are immediately available. Does not scroll down to induce more results to be loaded.
    An extremely expensive function. Call as infrequently as possible."""
    encoded = quote_plus(search_term)
    driver.get(SEARCH_BASE_URL + encoded)

    try:
        # Wait until all needed search results in the current screen have been loaded
        rough_results = WebDriverWait(driver, WAIT_TIMEOUT).until(
                            EC.presence_of_all_elements_located(
                                (By.CLASS_NAME, SIMPLE_SEARCH_RESULT_CLASS_FINGERPRINT)))

        # There's an anchor sub-element of each result that holds the information we need
        links = [raw_result.find_element_by_tag_name("a")
                 for raw_result in rough_results]

    # Youtube gave us the other, tiled format instead of the list format
    # It appears to be random though, and is difficult to induce.
    except TimeoutException:
        print("Falling back to tiled way...s")
        links = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, FALLBACK_SEARCH_RESULT_CLASS_FINGERPRINT)))

    return [(e.get_attribute("title"), e.get_attribute("href"))
            for e in links]
