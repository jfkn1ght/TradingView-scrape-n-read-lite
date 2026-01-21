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

# ------------------ Default URL ------------------
DEFAULT_URL = "https://www.tradingview.com/news-flow/?market=etf,crypto,forex,index,futures,bond,corp_bond,economic"

# ------------------ Load URL from external file with fallback ------------------
BASE_DIR = Path(__file__).resolve().parent
URL_FILE = BASE_DIR / "Scrape-n-Read_LITE_URL.txt"

URL = DEFAULT_URL  # Start with default

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

# ------------------ Main async loop ------------------
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Track seen headlines with provider + timestamp
        seen = set()

        # Initial load
        await page.goto(URL, wait_until="domcontentloaded")
        await scroll_page(page)

        # Initial output
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
                    provider = item["provider"]

                    if sys.platform == "win32":
                        playsound("C:/Windows/Media/chimes.wav")
                    elif sys.platform == "darwin": # macOS 
                        sound = "/System/Library/Sounds/Glass.aiff"
                    elif sys.platform.startswith("linux"):
                        sound = "/usr/share/sounds/freedesktop/stereo/complete.oga"

                    print(f"[{ts}] - {item['headline']} ({provider})")
                    seen.add(unique_id)

                    # TTS reads headline only
                    engine.say(item['headline'])
                    while engine.isBusy():
                        engine.iterate()
                        time.sleep(0.1)

# ------------------  Main ------------------
if __name__ == "__main__":
    asyncio.run(main())
