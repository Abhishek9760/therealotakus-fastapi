from fastapi import FastAPI
from enum import Enum
from anime_scraper import AnimeScraper
from typing import Optional

app = FastAPI()


@app.get('/')
async def home():
    return {'message': 'welcome'}


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


@app.get("/episodes")
async def get_episodes(source: str):
    anime_obj = AnimeScraper()
    eps = anime_obj.get_episodes(source)
    return {
        "episodes": anime_obj.episodes,
    }


@app.get('/episode')
async def get_episode(episode_link: str):
    anime_obj = AnimeScraper()
    return anime_obj.get_download_link(episode_link)
