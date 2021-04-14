import logging

import pyppeteer
from pyppeteer.errors import TimeoutError
from requests_html import HTML, AsyncHTMLSession
from typing import List, Tuple
from urllib.parse import quote_plus

OLD_SEARCH_RESULT_CLASS_FINGERPRINT = ".text-wrapper.style-scope.ytd-video-renderer"
SIMPLE_SEARCH_RESULT_CLASS_FINGERPRINT = ".yt-simple-endpoint.style-scope.ytd-video-renderer"
FALLBACK_SEARCH_RESULT_CLASS_FINGERPRINT = ".yt-simple-endpoint.style-scope.ytd-rich-grid-media"

SEARCH_BASE = "https://www.youtube.com/results?search_query="

RENDER_TIMEOUT_SECS = 10


# Because attempting to handle signals on threads other than the main is an error, and the server is multithreaded.
# The manually created and set browser in the function below is a hack to change the internal settings.
OPTIONS = {"handleSIGINT": False,
           "handleSIGTERM": False,
           "handleSIGHUP": False}

async def get_search_results_async(query: str) -> List[Tuple[str, str]]:
    encoded_query = quote_plus(query)
    session = None
    try:
        browser = await pyppeteer.launch(ignoreHTTPSErrors=False, headless=True,
                                         args=['--no-sandbox'], options=OPTIONS)

        session = AsyncHTMLSession(browser_args=OPTIONS)
        session._browser = browser

        response = await session.get(SEARCH_BASE + encoded_query)
        html: HTML = response.html
        await html.arender(timeout=RENDER_TIMEOUT_SECS)
        attrs = (link.attrs for link in html.find(SIMPLE_SEARCH_RESULT_CLASS_FINGERPRINT))

        if attrs:
            pairs = ((attr['title'], attr['href']) for attr in attrs)  # Extract the title and hrefs
            return [(title, href.split("=")[-1]) for title, href in pairs]  # Get the video codes out of the pairs
        else:
            logging.warning(f"Scraping return 0 results for {query}.")
            return []
    except TimeoutError:
        logging.warning(f"Rendering of request for {query} timed out (max {RENDER_TIMEOUT_SECS} seconds).")
        return []
    finally:
        if session:
            await session.close()

