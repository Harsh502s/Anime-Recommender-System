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
TEMP_CSV = "anime_data_temp.csv"
STATE_FILE = "scrape_state.json"
CHUNK_SIZE = 100
CONCURRENCY_LIMIT = 30

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
    # Random jitter to mimic human behavior
    await asyncio.sleep(random.uniform(0.15, 0.5))

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

async def discover_anime_urls(client: httpx.AsyncClient, total_pages: int, semaphore: asyncio.Semaphore) -> List[str]:
    logger.info(f"Collecting URLs from {total_pages} pages sequentially...")
    anime_urls = []

    for i in range(1, total_pages + 1):
        url = f"{LANDING_PAGE_URL}page/{i}" if i != 1 else LANDING_PAGE_URL
        try:
            resp = await safe_get(client, url)
            soup = BeautifulSoup(resp.content, "html.parser")
            for anime in soup.find_all("div", class_="ani"):
                if "poster" in anime.get("class", []):
                    link = anime.find("a")["href"]
                    anime_urls.append(BASE_URL + link)
        except Exception as e:
            logger.error(f"Failed to scrape list page {i}: {e}")

    return anime_urls

def extract_label_value(soup: BeautifulSoup, label_text: str) -> str:
    element = soup.find(lambda tag: tag.name == "div" and label_text in tag.text)
    if element:
        value_elem = element.find("span") or element.find("a")
        if value_elem:
            return value_elem.text.strip()
    return "NA"

def extract_label_list(soup: BeautifulSoup, label_text: str) -> List[str]:
    element = soup.find(lambda tag: tag.name == "div" and label_text in tag.text)
    if element:
        links = element.find_all("a")
        if links:
            return [link.text.strip() for link in links]
    return ["NA"]

async def fetch_anime_details(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore) -> Optional[Dict[str, Any]]:
    async with semaphore:
        try:
            resp = await safe_get(client, url)
            soup = BeautifulSoup(resp.content, "html.parser")

            # Poster
            poster_div = soup.find("div", class_="poster")
            anime_poster = poster_div.find("img")["src"] if poster_div and poster_div.find("img") else "NA"

            # Title
            title_elem = soup.find("h1", class_="title d-title")
            anime_title = title_elem.text.strip() if title_elem else "NA"

            # Overview
            overview_elem = soup.find("div", class_="description") or soup.find("div", class_="plot")
            anime_overview = overview_elem.text.strip() if overview_elem else "NA"

            # Details
            return {
                "url": url,
                "anime_poster": anime_poster,
                "anime_title": anime_title,
                "anime_overview": anime_overview,
                "anime_mal_score": extract_label_value(soup, "MAL Score:"),
                "anime_studio": extract_label_value(soup, "Studios:"),
                "anime_producer": extract_label_list(soup, "Producers:"),
                "anime_genres": extract_label_list(soup, "Genres:"),
            }
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None

async def main():
    start_time = datetime.now()
    # Load state if exists
    start_index = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            start_index = json.load(f).get("last_index", 0)
            logger.info(f"Resuming from index {start_index}")

    async with httpx.AsyncClient(http2=True) as client:
        # Initialize Semaphore first
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

        # 1. URL Discovery
        try:
            total_pages = await get_total_pages(client)
            anime_urls = await discover_anime_urls(client, total_pages, semaphore)
            logger.info(f"Total anime URLs discovered: {len(anime_urls)}")
        except Exception as e:
            logger.error(f"Critical error during discovery: {e}")
            return

        # 2. Detail Extraction
        tasks = [fetch_anime_details(client, url, semaphore) for url in anime_urls[start_index:]]

        buffer = []
        processed_count = start_index

        # Use tqdm for progress tracking
        buffer = []
        processed_count = start_index

        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scraping Anime"):
            result = await coro
            if result:
                buffer.append(result)

            processed_count += 1

            # Checkpointing to TEMP file
            if len(buffer) >= CHUNK_SIZE:
                df = pd.DataFrame(buffer)
                # Append to temp file (header only if file doesn't exist)
                df.to_csv(TEMP_CSV, mode='a', index=False, header=not os.path.exists(TEMP_CSV))

                # Save state
                with open(STATE_FILE, 'w') as f:
                    json.dump({"last_index": processed_count}, f)

                buffer = []
                logger.info(f"Checkpoint reached: {processed_count} processed. Saved to temp.")

        # Final flush to TEMP
        if buffer:
            df = pd.DataFrame(buffer)
            df.to_csv(TEMP_CSV, mode='a', index=False, header=not os.path.exists(TEMP_CSV))
            with open(STATE_FILE, 'w') as f:
                json.dump({"last_index": processed_count}, f)

        # Final Step: Atomic Rename Temp -> Final
        if os.path.exists(TEMP_CSV):
            logger.info(f"Finalizing data... renaming {TEMP_CSV} to {OUTPUT_CSV}")
            if os.path.exists(OUTPUT_CSV):
                os.remove(OUTPUT_CSV)
            os.rename(TEMP_CSV, OUTPUT_CSV)

    logger.info("Scraping complete!")
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Total time taken: {duration}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user. State saved.")
