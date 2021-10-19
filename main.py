import models
from fastapi import FastAPI
from enum import Enum
from anime_scraper import AnimeScraper
from typing import Optional
from functions import streamsb
from database import SessionLocal, engine
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()

def create_app(db: Session, message: str, show_message: bool, version: str):
    db_app = models.App(message=message, show_message=show_message, version=version)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

def get_app_data(db: Session):
    return db.query(models.App).order_by(models.App.id.desc()).first()


def update_installs(db: Session):
    try:
        first_item =  db.query(models.AppInstall).first()
        first_item.total_install += 1
        db.commit()
        db.refresh(first_item)
    except:
        db_app_install = models.AppInstall(total_install = 0)
        db.add(db_app_install)
        db.commit()
        db.refresh(db_app_install)

def get_app_update_installs(db: Session):
    return db.query(models.AppInstall).first()

@app.get('/')
async def home():
    return {'message': 'welcome'}

@app.get('/app/info')
async def get_app_info():
    db = next(get_db())
    data = get_app_data(db)
    return {
        "message":data.message,
        "show_message": data.show_message,
        "version": data.version
    }

@app.get('/app')
async def set_app_info(message: str, show:bool, version:str):
    create_app(next(get_db()), message, show, version)
    return {"message": "Enjoy watching Anime for free :)", "show": False, "version":"1.6"}

@app.get('/app/install/add')
async def app_install():
    db = next(get_db())
    update_installs(db)
    return {'status': 'done'}

@app.get('/app/install')
async def get_app_install():
    db = next(get_db())
    total_install = get_app_update_installs(db)
    if(total_install):
        return {'total_install': total_install.total_install}
    return {'status': 'go to /app/install/add first'}



@app.get('/app/install/reset')
async def app_install_reset():
    db = next(get_db())
    total_install = db.query(models.AppInstall).delete()
    db.commit()
    return {'status': 'done'}

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
