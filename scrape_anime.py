import asyncio
import random
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import warnings as w

w.filterwarnings("ignore")

# --- Configuration ---
BASE_URL = "https://aniwaves.ru"
LANDING_PAGE_URL = f"{BASE_URL}/az-list/"
OUTPUT_CSV = "anime_data.csv"
CHUNK_SIZE = 100
CONCURRENCY_LIMIT = 12 # Balanced for speed vs anti-bot risk

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- Resilience Logic ---

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
)
async def safe_get(client: httpx.AsyncClient, url: str):
    """Fetch URL with retry logic, random User-Agent, and automatic redirect following."""
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
    response.raise_for_status()
    return response

# --- Core Logic ---

async def get_total_pages(client: httpx.AsyncClient) -> int:
    logger.info("Determining total pages...")
    resp = await safe_get(client, LANDING_PAGE_URL)
    soup = BeautifulSoup(resp.content, "lxml")
    nav = soup.find("nav", class_='navigation')
    if not nav:
        raise ValueError("Could not find navigation element on landing page.")
    last_page_link = nav.find_all("li")[-1].find("a")["href"]
    return int(last_page_link.split("/")[-1])

async def discover_anime_urls(client: httpx.AsyncClient, total_pages: int) -> List[str]:
    logger.info(f"Collecting URLs from {total_pages} pages concurrently...")

    # Use a semaphore to avoid overwhelming the server during discovery
    discovery_semaphore = asyncio.Semaphore(5)

    async def fetch_page_urls(page_num: int) -> List[str]:
        async with discovery_semaphore:
            url = f"{LANDING_PAGE_URL}all/page/{page_num}" if page_num != 1 else LANDING_PAGE_URL
            try:
                resp = await safe_get(client, url)
                soup = BeautifulSoup(resp.content, "html.parser")

                page_anime = []
                for anime in soup.find_all("div", class_="ani"):
                    if "poster" in anime.get("class", []):
                        link = anime.find("a")["href"]
                        if link:
                            full_url = BASE_URL + link if link.startswith("/") else link
                            page_anime.append(full_url)
                return page_anime
            except Exception as e:
                logger.error(f"Failed to scrape list page {page_num}: {e}")
                return []

    # Create tasks for all pages
    tasks = [fetch_page_urls(i) for i in range(1, total_pages + 1)]

    # Gather results (will be a list of lists)
    results = await asyncio.gather(*tasks)

    # Flatten the list of lists
    anime_urls = [url for page_list in results for url in page_list]

    return anime_urls

def extract_label_value(soup: BeautifulSoup, label_text: str) -> str:
    """Extract value for label like 'Scores:', 'Studios:'."""
    # Find div.bmeta which contains the details
    bmeta = soup.find("div", class_="bmeta")
    if not bmeta:
        return "NA"

    # Search within bmeta divs for the label
    for meta_div in bmeta.find_all("div", class_="meta"):
        for div in meta_div.find_all("div"):
            # Check if this div contains our label
            if label_text in div.get_text():
                # The structure is: Label: <span>Value</span>
                # Get all text after the label
                full_text = div.get_text(strip=True)
                idx = full_text.find(label_text)
                if idx != -1:
                    value = full_text[idx + len(label_text):].strip()
                    # Clean up: remove trailing text like "/ 64,281 reviews"
                    if "/" in value:
                        value = value.split("/")[0].strip()
                    # Remove trailing content that starts with punctuation
                    for char in [",", ")", "(", "[", "#"]:
                        if char in value:
                            value = value.split(char)[0].strip()
                    return value if value else "NA"
    return "NA"

def extract_label_list(soup: BeautifulSoup, label_text: str) -> List[str]:
    """Extract list of values for label like 'Genres:', 'Producers:'."""
    bmeta = soup.find("div", class_="bmeta")
    if not bmeta:
        return ["NA"]

    for meta_div in bmeta.find_all("div", class_="meta"):
        for div in meta_div.find_all("div"):
            if label_text in div.get_text():
                full_text = div.get_text(strip=True)
                idx = full_text.find(label_text)
                if idx != -1:
                    value = full_text[idx + len(label_text):].strip()
                    # For Genres: split by comma
                    if label_text == "Genres:":
                        items = [item.strip() for item in value.split(",") if item.strip()]
                        return items if items else ["NA"]
                    # For Producers: split by comma
                    if label_text == "Producers:":
                        items = [item.strip() for item in value.split(",") if item.strip()]
                        return items if items else ["NA"]
    return ["NA"]

async def fetch_anime_details(client: httpx.AsyncClient, url: str) -> Optional[Dict[str, Any]]:
    try:
        resp = await safe_get(client, url)
        soup = BeautifulSoup(resp.content, "html.parser")

        # Poster
        poster_div = soup.find("div", class_="poster")
        anime_poster = poster_div.find("img")["src"] if poster_div and poster_div.find("img") else "NA"

        # Title
        title_elem = soup.find("h1", class_="title d-title")
        anime_title = title_elem.text.strip() if title_elem else "NA"

        # Overview - check multiple possible structures
        overview_elem = soup.find("div", class_="description") or soup.find("div", class_="plot") or soup.find("div", class_="synopsis")
        anime_overview = "NA"
        if overview_elem:
            # Try to find text content within the overview
            text_content = overview_elem.find("div", class_="text content")
            if text_content:
                anime_overview = text_content.get_text(strip=True)
            else:
                anime_overview = overview_elem.get_text(strip=True)

        # Details
        data = {
            "url": url,
            "anime_poster": anime_poster,
            "anime_title": anime_title,
            "anime_overview": anime_overview,
            "anime_mal_score": extract_label_value(soup, "Scores:"),
            "anime_studio": extract_label_value(soup, "Studios:"),
            "anime_producer": extract_label_list(soup, "Producers:"),
            "anime_genres": extract_label_list(soup, "Genres:"),
        }

        # Validation: Ensure critical fields are present
        if data["anime_title"] == "NA" or data["anime_poster"] == "NA" or data["anime_overview"] == "NA":
            logger.warning(f"Critical data missing for {url}: title={data['anime_title']}, poster={data['anime_poster']}, overview={data['anime_overview']}")
            # We still return the data, but the warning flags it for audit

        return data
    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        return None

async def csv_writer(results_queue: asyncio.Queue):
    """Background task to write results to CSV in buffered batches."""
    buffer = []
    processed_count = 0

    while True:
        item = await results_queue.get()
        if item is None: # Sentinel to stop
            if buffer:
                df = pd.DataFrame(buffer)
                df.to_csv(OUTPUT_CSV, mode='a', index=False, header=not os.path.exists(OUTPUT_CSV))
            results_queue.task_done()
            break

        if item:
            buffer.append(item)
            processed_count += 1

        # Write to CSV every CHUNK_SIZE items
        if len(buffer) >= CHUNK_SIZE:
            df = pd.DataFrame(buffer)
            df.to_csv(OUTPUT_CSV, mode='a', index=False, header=not os.path.exists(OUTPUT_CSV))
            logger.info(f"Writer: Saved {processed_count} total items to {OUTPUT_CSV}")
            buffer = []

        results_queue.task_done()

async def worker(client: httpx.AsyncClient, url_queue: asyncio.Queue, results_queue: asyncio.Queue):
    """Worker that pulls URLs from queue and fetches details."""
    while True:
        url = await url_queue.get()
        if url is None: # Sentinel to stop
            url_queue.task_done()
            break

        result = await fetch_anime_details(client, url)
        await results_queue.put(result)
        url_queue.task_done()

async def main():
    start_time = datetime.now()

    # 1. Setup Queues
    url_queue = asyncio.Queue()
    results_queue = asyncio.Queue()

    async with httpx.AsyncClient(http2=True) as client:
        # 2. URL Discovery
        try:
            total_pages = await get_total_pages(client)
            anime_urls = await discover_anime_urls(client, total_pages)
            logger.info(f"Total anime URLs discovered: {len(anime_urls)}")

            for url in anime_urls:
                await url_queue.put(url)
        except Exception as e:
            logger.error(f"Critical error during discovery: {e}")
            return

        # 3. Start Worker Pool and Writer
        workers = [asyncio.create_task(worker(client, url_queue, results_queue))
                   for _ in range(CONCURRENCY_LIMIT)]
        writer_task = asyncio.create_task(csv_writer(results_queue))

        # 4. Wait for URL queue to be fully processed
        await url_queue.join()

        # 5. Shutdown workers
        for _ in range(CONCURRENCY_LIMIT):
            await url_queue.put(None)
        await asyncio.gather(*workers)

        # 6. Shutdown writer
        await results_queue.put(None)
        await writer_task

    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Scraping complete! Total time taken: {duration}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user. State saved.")
