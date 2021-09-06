import requests
from lxml import html
from urllib.parse import urlparse


SERVICES = {"gogo": "https://gogoanime.pe//search.html?keyword={query}"}


class AnimeScraper:
    def __init__(self, service="gogo", query=""):
        self.query = query
        self.service = "gogo"
        self.source = None
        self.i = 0
        self.total_episodes = 0
        self.total_res = 0
        self.episode_gateway_url = "https://ajax.gogo-load.com/ajax/load-list-episode?ep_start=0&ep_end={total_ep}&id={movie_id}&default_ep=0&alias={alias_name}"
        self.episodes = None
        self.alias_name = None
        self.anime_list = self.scrape(query=query)

    def __iter__(self):
        return self

    def __next__(self):
        if self.i > self.total_res:
            raise StopIteration
        else:
            self.i += 1
            return next(self.anime_list)

    def scrape_gogo_anime_list(self, url):
        res = requests.get(url)
        if res.status_code != 200:
            raise ConnectionError("Your internet might be slow :(")

        tree = html.fromstring(res.text)
        anime_list = tree.xpath(
            "//div[@class='last_episodes']//ul")[0].xpath(".//li")
        self.total_res = len(anime_list)
        l = self.anime_list_items_parser(anime_list)
        return l

    def anime_list_items_parser(self, anime_list):
        for item in anime_list:
            image = item.xpath(".//img//@src")[0]
            name = item.xpath(".//p[@class='name']//text()")[0]
            source = self._refine_url(item.xpath(
                ".//p[@class='name']//@href")[0])
            total_episodes = self.anime_list_item_parser(source)
            self.source = source
            self.total_episodes = int(total_episodes)
            yield {
                "image": image,
                "name": name,
                "source": source,
                "total_episodes": total_episodes,
            }

    def anime_list_item_parser(self, link):
        if not (link and self._check_url(link)):
            raise ValueError("Invalid link")
        res = requests.get(link)
        tree = html.fromstring(res.text)
        total_episodes = (
            tree.xpath("//ul[@id='episode_page']//li[last()]")[0]
            .text_content()
            .strip()
            .split("-")[-1]
        )
        return total_episodes

    def scrape(self, service="gogo", query=""):
        query = self.query or query
        if not query:
            return
        func = getattr(self, f"scrape_{service}_anime_list")
        url = SERVICES["gogo"].format(query=query)
        return func(url)

    def get_download_link(self, url):
        res = requests.get(url)
        if res.status_code != 200:
            raise ConnectionError("Your internet might be slow:(")
        tree = html.fromstring(res.text)
        download_link = tree.xpath(".//li[@class='dowloads']//a//@href")[0]
        download_links = self.parse_download_link(download_link)
        return download_links

    def parse_download_link(self, link):
        res = requests.get(link)
        tree = html.fromstring(res.text)
        download_links = tree.xpath("//div[@class='mirror_link']")[0].xpath(
            ".//a//@href"
        )
        quality = tree.xpath(
            "//div[@class='mirror_link']")[0].xpath(".//a//text()")
        quality = [self._parse_quality_name(i) for i in quality]
        return dict(zip(quality, download_links))

    def _parse_quality_name(self, text):
        i1 = text.index("P")
        i2 = text.index("(")
        res = text[i2 + 1: i1 + 1]
        return res

    def _refine_url(self, url):
        if self._check_url(url):
            return url
        return "https://" + urlparse(SERVICES["gogo"]).netloc + url

    def _check_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def get_episodes(self, source):
        res = requests.get(source)
        tree = html.fromstring(res.text)
        movie_id = tree.xpath("//input[@id='movie_id']//@value")[0]
        alias_name = tree.xpath("//input[@id='alias_anime']//@value")[0]
        self.alias_name = alias_name
        url = self.episode_gateway_url.format(
            total_ep=self.total_episodes, movie_id=movie_id, alias_name=alias_name
        )
        return self.get_episodes_parse(url)

    def get_episodes_parse(self, url):
        res = requests.get(url)
        tree = html.fromstring(res.text)
        ep_names = [
            i.strip()
            for i in tree.xpath("//div[@class='name']/text()[not(parent::span)]")
        ]
        ep_links = [self._refine_url(i.strip())
                    for i in tree.xpath("//a//@href")]
        eps = dict(zip(ep_names, ep_links))
        eps = dict(sorted(eps.items(), key=lambda item: float(item[0])))
        self.episodes = eps
        return self.episodes
