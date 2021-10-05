from fastapi import FastAPI
from enum import Enum
from anime_scraper import AnimeScraper
from typing import Optional
from functions import streamsb

app = FastAPI()

@app.get('/')
async def home():
    return {'message': 'welcome'}


@app.get('/app')
async def get_app_info():
    return {"message": "Welcome, Enjoy Anime in quality.", "show": True, "version":"1.5"}

@app.get("/search/{q}")
async def search_anime(q: str):
    anime_obj = AnimeScraper(query=q)
    res = []
    if anime_obj.total_res > 10:
        for i in range(10):
            res.append(next(anime_obj))
    else:
        res = [i for i in anime_obj]
    return res


@app.get('/episode')
async def get_episode(episode_link: str):
    anime_obj = AnimeScraper()
    download_links = anime_obj.get_download_link(episode_link)
    mirrors = download_links[1]
    streamsb_link = mirrors.get('StreamSB')
    if streamsb_link and not download_links[0]:
        streamsb_urls = streamsb.get_streamsb(streamsb_link)
        download_links[1]["StreamSB"] = streamsb_urls
    return download_links

@app.get('/popular')
async def get_popular(page: Optional[int]=1):
    anime_obj = AnimeScraper()
    return anime_obj.get_popular(page=page)

@app.get('/anime')
async def get_anime_info(source: str):
    anime_obj = AnimeScraper()
    return anime_obj.anime_list_item_parser(source)

@app.get('/genre')
async def get_genre_list():
    anime_obj = AnimeScraper()
    return anime_obj.get_genre_list()

@app.get('/genre/{genre}')
async def get_genre(genre: str, page: Optional[int]=1):
    anime_obj = AnimeScraper()
    formatted_genre = genre.lower().replace(' ', '-')
    url = f"https://gogoanime.pe/genre/{formatted_genre}?page={page}"
    return list(anime_obj.scrape_gogo_anime_list(url))