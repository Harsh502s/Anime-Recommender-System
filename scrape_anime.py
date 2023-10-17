import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import requests
from tqdm import tqdm
import warnings as w

w.filterwarnings("ignore")


no_of_page = int(
    BeautifulSoup(requests.get("https://aniwatch.to/az-list").content, "lxml")
    .find("nav", attrs={"aria-label": "Page navigation"})
    .find_all("li")[-1]
    .find("a")["href"]
    .split("=")[1]
)
landing_page_url = "https://aniwatch.to/az-list"
page_urls = [
    f"{landing_page_url}/?page={i}" if i != 1 else landing_page_url
    for i in range(1, no_of_page + 1)
]

# Scraping the data from all the pages

anime_urls = []

for url in tqdm(page_urls):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # Getting the url for the anime page

    for anime in soup.find_all("div", class_="film-poster"):
        anime = anime.find("a")["href"]
        page = "https://aniwatch.to" + anime
        anime_urls.append(page)
        pass
    pass

anime_url = pd.DataFrame(anime_urls, columns=["anime_url"])
anime_url.to_csv("anime_url.csv", index=False)


# def process_url(url):
#     soup = BeautifulSoup(requests.get(url).content, "html.parser")

#     anime_poster = soup.find("div", class_="film-poster").find("img")["src"]

#     # Getting the name of the anime

#     anime_title = soup.find("h2", class_="film-name dynamic-name").text

#     # Getting the overview of the anime

#     anime_overview = anime_overview = (
#         soup.find("div", class_="item item-title w-hide")
#         .find("div", class_="text")
#         .text
#     )

#     # Creating an object of the div containing all the details of the anime

#     soup = soup.find("div", class_="anisc-info")

#     # Extract MAL Score
#     mal_score_element = soup.find("span", {"class": "item-head"}, text="MAL Score:")
#     anime_mal_score = (
#         mal_score_element.find_next_sibling("span", {"class": "name"}).text.strip()
#         if mal_score_element
#         else "NA"
#     )

#     # Extract Studios
#     studios_element = soup.find("span", {"class": "item-head"}, text="Studios:")
#     anime_studio = (
#         studios_element.find_next("a", {"class": "name"}).text.strip()
#         if studios_element
#         else "NA"
#     )

#     # Extract Producers
#     producers_element = soup.find("span", {"class": "item-head"}, text="Producers:")
#     anime_producer = (
#         [
#             producer.text.strip()
#             for producer in producers_element.find_next_siblings("a")
#         ]
#         if producers_element
#         else ["NA"]
#     )

#     # Extract Genres
#     genres_element = soup.find("span", {"class": "item-head"}, text="Genres:")
#     anime_genres = (
#         [genre.text.strip() for genre in genres_element.find_next_siblings("a")]
#         if genres_element
#         else ["NA"]
#     )

#     return (
#         anime_poster,
#         anime_title,
#         anime_overview,
#         anime_mal_score,
#         anime_studio,
#         anime_producer,
#         anime_genres,
#     )


# def create_df_parallel(anime_urls, num_threads=4):
#     anime_poster_list = []
#     anime_title_list = []
#     anime_overview_list = []
#     anime_mal_score_list = []
#     anime_studio_list = []
#     anime_producer_list = []
#     anime_genres_list = []

#     with ThreadPoolExecutor(max_workers=num_threads) as executor:
#         results = executor.map(process_url, anime_urls)

#         for result in results:
#             anime_poster_list.append(result[0])
#             anime_title_list.append(result[1])
#             anime_overview_list.append(result[2])
#             anime_mal_score_list.append(result[3])
#             anime_studio_list.append(result[4])
#             anime_producer_list.append(result[5])
#             anime_genres_list.append(result[6])

#     anime_dict = {
#         "anime_poster": anime_poster_list,
#         "anime_title": anime_title_list,
#         "anime_overview": anime_overview_list,
#         "anime_mal_score": anime_mal_score_list,
#         "anime_studio": anime_studio_list,
#         "anime_producer": anime_producer_list,
#         "anime_genres": anime_genres_list,
#     }

#     anime_df = pd.DataFrame(anime_dict)
#     return anime_df


# anime_df = create_df_parallel(anime_urls)
# anime_df.head()
# anime_df.to_csv("anime_data.csv", index=False)
