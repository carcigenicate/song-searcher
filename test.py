import pyppeteer
from requests_html import AsyncHTMLSession, HTML
from asyncio import run
from threading import Thread

OPTIONS = {"handleSIGINT": False,
           "handleSIGTERM": False,
           "handleSIGHUP": False}

async def func():
    session = None
    try:
        browser = await pyppeteer.launch(ignoreHTTPSErrors=False, headless=True,
                                         args=['--no-sandbox'], options=OPTIONS)

        session = AsyncHTMLSession(browser_args=OPTIONS)
        session._browser = browser

        response = await session.get("http://www.youtube.com")
        html: HTML = response.html
        await html.arender()
        print(html.links)

    finally:
        if session:
            await session.close()

def main():
    t = Thread(target=lambda: run(func()))
    t.start()
    t.join()
    # run(func())
