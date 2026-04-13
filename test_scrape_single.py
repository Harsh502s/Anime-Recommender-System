"""Test script: scrape only page 1, first anime, validate data."""
import asyncio
import logging
import json
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import random
import warnings as w

w.filterwarnings("ignore")

# --- Config ---
BASE_URL = "https://aniwaves.ru"
LANDING_PAGE_URL = f"{BASE_URL}/az-list/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Resilience (same as main script) ---
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
)
async def safe_get(client: httpx.AsyncClient, url: str):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    await asyncio.sleep(random.uniform(0.15, 0.5))
    response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
    response.raise_for_status()
    return response

# --- Helper functions (from scrape_anime.py) ---
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

def extract_label_list(soup: BeautifulSoup, label_text: str) -> list:
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

# --- Test Logic ---
async def get_first_anime_url(client: httpx.AsyncClient) -> tuple[str, BeautifulSoup]:
    """Get URL and soup of first anime on page 1."""
    logger.info("Fetching landing page (page 1)...")
    resp = await safe_get(client, LANDING_PAGE_URL)
    soup = BeautifulSoup(resp.content, "html.parser")

    # Find first anime div
    anime_divs = soup.find_all("div", class_="ani")
    for anime in anime_divs:
        if "poster" in anime.get("class", []):
            link = anime.find("a")["href"]
            full_url = BASE_URL + link
            logger.info(f"First anime URL: {full_url}")
            return full_url, soup

    raise ValueError("No anime found on landing page")

async def scrape_first_anime(client: httpx.AsyncClient) -> dict:
    """Scrape first anime details and return validated data."""
    # Get URL from landing page
    anime_url, list_page_soup = await get_first_anime_url(client)

    # Scrape detail page
    logger.info("Fetching anime details...")
    resp = await safe_get(client, anime_url)
    soup = BeautifulSoup(resp.content, "html.parser")

    # Extract data
    poster_div = soup.find("div", class_="poster")
    anime_poster = poster_div.find("img")["src"] if poster_div and poster_div.find("img") else "NA"

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

    data = {
        "url": anime_url,
        "anime_poster": anime_poster,
        "anime_title": anime_title,
        "anime_overview": anime_overview,
        "anime_mal_score": extract_label_value(soup, "Scores:"),  # Page uses "Scores:" not "MAL Score:"
        "anime_studio": extract_label_value(soup, "Studios:"),  # Use correct label with better extraction
        "anime_producer": extract_label_list(soup, "Producers:"),
        "anime_genres": extract_label_list(soup, "Genres:"),
    }

    return data, list_page_soup, soup

def validate_data(data: dict) -> list:
    """Validate scraped data. Return list of (field, value, status)."""
    issues = []

    # Title validation
    if not data["anime_title"] or data["anime_title"] == "NA":
        issues.append(("anime_title", data["anime_title"], "FAIL: empty or NA"))
    else:
        issues.append(("anime_title", data["anime_title"][:50] + "...", "PASS"))

    # Poster validation
    if not data["anime_poster"] or data["anime_poster"] == "NA":
        issues.append(("anime_poster", data["anime_poster"], "FAIL: empty or NA"))
    else:
        issues.append(("anime_poster", data["anime_poster"], "PASS"))

    # Overview validation
    if not data["anime_overview"] or data["anime_overview"] == "NA":
        issues.append(("anime_overview", data["anime_overview"][:50] + "...", "FAIL: empty or NA"))
    else:
        issues.append(("anime_overview", data["anime_overview"][:50] + "...", "PASS"))

    # MAL Score (NA is acceptable)
    issues.append(("anime_mal_score", data["anime_mal_score"], "PASS" if data["anime_mal_score"] != "NA" else "PASS (NA acceptable)"))

    # Studio (NA is acceptable)
    issues.append(("anime_studio", data["anime_studio"], "PASS" if data["anime_studio"] != "NA" else "PASS (NA acceptable)"))

    # Producers (list, ["NA"] is acceptable)
    issues.append(("anime_producer", data["anime_producer"], "PASS" if data["anime_producer"] != ["NA"] else "PASS (empty acceptable)"))

    # Genres (list, ["NA"] is acceptable)
    issues.append(("anime_genres", data["anime_genres"], "PASS" if data["anime_genres"] != ["NA"] else "PASS (empty acceptable)"))

    return issues

async def main():
    start = __import__("datetime").datetime.now()

    async with httpx.AsyncClient(http2=True) as client:
        try:
            data, list_page_soup, detail_page_soup = await scrape_first_anime(client)
        except Exception as e:
            logger.error(f"Failed: {e}")
            return

    # Save to CSV
    df = pd.DataFrame([data])
    csv_path = "test_anime_data.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Data saved to {csv_path}")

    # Print results
    print("\n" + "=" * 60)
    print("SCRAPED DATA:")
    print("=" * 60)
    print(json.dumps(data, indent=2, default=str))

    # Validate
    print("\n" + "=" * 60)
    print("VALIDATION:")
    print("=" * 60)
    issues = validate_data(data)
    all_pass = True
    for field, value, status in issues:
        print(f"[{status}] {field}: {value}")
        if "FAIL" in status:
            all_pass = False

    print("\n" + "=" * 60)
    print(f"RESULT: {'ALL TESTS PASSED' if all_pass else 'TESTS FAILED'}")
    print("=" * 60)

    end = __import__("datetime").datetime.now()
    print(f"Duration: {end - start}")

if __name__ == "__main__":
    asyncio.run(main())
