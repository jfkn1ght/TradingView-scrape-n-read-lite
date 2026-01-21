import os
import sys
import pyttsx3
import time
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timezone
from playsound3 import playsound
from pathlib import Path

# ------------------ Cross-platform console title ------------------
def set_console_title(title):
    if os.name == "nt":  # Windows
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:  # Linux / macOS
        sys.stdout.write(f"\33]0;{title}\a")
        sys.stdout.flush()

set_console_title("TradingView Headline Scrape-N-Read Lite by @JFKN1GHT")

# ------------------ Base directory (script or EXE safe) ------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# ------------------ Default URL ------------------
DEFAULT_URL = "https://www.tradingview.com/news-flow/?market=etf,crypto,forex,index,futures,bond,corp_bond,economic"

# ------------------ Load URL from external file with fallback ------------------
URL_FILE = BASE_DIR / "Scrape-n-Read_LITE_URL.txt"
URL = DEFAULT_URL

if URL_FILE.exists():
    with URL_FILE.open("r", encoding="utf-8") as f:
        file_url = f.read().strip()
    if file_url.startswith(("http://", "https://")):
        URL = file_url
    else:
        print(f"Invalid URL in {URL_FILE.name}, using default URL.")
else:
    print(f"{URL_FILE.name} not found, using default URL.")

print(f"Using URL: {URL}")

# ------------------ Constants ------------------
HEADLINE_BLOCK_SELECTOR = "article"

# ------------------ Text-to-speech setup ------------------
engine = pyttsx3.init()
engine.startLoop(False)

# ------------------ Time formatting ------------------
def format_event_time(event_time_str):
    dt = datetime.strptime(event_time_str, "%a, %d %b %Y %H:%M:%S GMT")
    dt = dt.replace(tzinfo=timezone.utc).astimezone()
    return dt.strftime("%I:%M %p")

# ------------------ Scraping Set-Up ------------------
async def scrape_headlines_with_time(page):
    await page.wait_for_selector(HEADLINE_BLOCK_SELECTOR, timeout=15000)

    return await page.eval_on_selector_all(
        HEADLINE_BLOCK_SELECTOR,
        """
        blocks => blocks.map(block => {
            const headlineEl = block.querySelector('div[data-qa-id="news-headline-title"]');
            const timeEl = block.querySelector('relative-time');
            const providerEl = block.querySelector('span.provider-e7vDzPX4 > span');

            if (!headlineEl || !timeEl) return null;

            return {
                headline: headlineEl.innerText.trim(),
                event_time: timeEl.getAttribute('event-time'),
                provider: providerEl ? providerEl.innerText.trim() : "Unknown"
            };
        }).filter(Boolean)
        """
    )

async def scroll_page(page, times=4, pause=0.8):
    for _ in range(times):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(pause)

# ------------------ Resolve bundled Chromium ------------------
def get_chromium_executable():
    """
    Returns path to bundled Chromium if running as EXE,
    otherwise returns None to let Playwright use its cache.
    """
    if getattr(sys, 'frozen', False):
        chromium_path = (
            BASE_DIR
            / "playwright-browsers"
            / "chromium"
            / "chrome-win"
            / "chrome.exe"
        )
        if not chromium_path.exists():
            raise FileNotFoundError(f"Chromium not found at {chromium_path}")
        return str(chromium_path)
    return None

# ------------------ Main async loop ------------------
async def main():
    chromium_exe = get_chromium_executable()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=chromium_exe
        )

        page = await browser.new_page()
        seen = set()

        await page.goto(URL, wait_until="domcontentloaded")
        await scroll_page(page)

        items = await scrape_headlines_with_time(page)
        for item in reversed(items):
            unique_id = f"{item['headline']}|{item['provider']}|{item['event_time']}"
            ts = format_event_time(item["event_time"])
            print(f"[{ts}] - {item['headline']} ({item['provider']})")
            seen.add(unique_id)

        print("\n--- LIVE FEED --- (Ctrl+C to quit)\n")

        while True:
            await asyncio.sleep(12)

            await page.reload(wait_until="domcontentloaded")
            await scroll_page(page)

            items = await scrape_headlines_with_time(page)

            for item in items:
                unique_id = f"{item['headline']}|{item['provider']}|{item['event_time']}"
                if unique_id not in seen:
                    ts = format_event_time(item["event_time"])
                    print(f"[{ts}] - {item['headline']} ({item['provider']})")
                    seen.add(unique_id)

                    # Windows-safe sound
                    if os.name == "nt":
                        #import winsound
                        #winsound.MessageBeep()
                        playsound("C:/Windows/Media/chimes.wav")

                    # Speak headline
                    engine.say(item['headline'])
                    while engine.isBusy():
                        engine.iterate()
                        time.sleep(0.1)

# ------------------ Main ------------------
if __name__ == "__main__":
    asyncio.run(main())
