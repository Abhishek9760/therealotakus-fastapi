import requests
from lxml import html
from urllib.parse import urlparse

SERVICES = {"gogo": "https://gogoanime.cm/search.html?keyword={query}"}

class AnimeScraper:
    def __init__(self, service="gogo", query=""):
        self.query = query
        self.service = "gogo"
        self.source = None
        self.i = 0
        self.total_episodes = 0
        self.total_res = 0
        self.episode_gateway_url = "https://ajax.gogo-load.com/ajax/load-list-episode?ep_start=0&ep_end={total_ep}&id={movie_id}&default_ep=0&alias={alias_name}"
        self.episodes = []
        self.alias_name = None
        self.anime_info = None
        self.headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"}
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
        res = requests.get(url, headers=self.headers)
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
            # total_episodes = self.anime_list_item_parser(source)
            self.source = source
            # self.total_episodes = int(total_episodes)
            yield {
                "image": image,
                "name": name,
                "source": source
                # "total_episodes": total_episodes,
                # "anime_info": self.anime_info
            }

    def anime_list_item_parser(self, link):
        if not (link and self._check_url(link)):
            raise ValueError("Invalid link")
        res = requests.get(link, headers=self.headers)
        tree = html.fromstring(res.text)
        total_episodes = (
            tree.xpath("//ul[@id='episode_page']//li[last()]")[0]
            .text_content()
            .strip()
            .split("-")[-1]
        )
        self.get_episodes(tree)

        self.anime_info = self.get_anime_info(tree)
        return {
            "total_episodes": total_episodes,
            "anime_info": self.anime_info,
            "episodes": self.episodes,
        }

    def scrape(self, service="gogo", query=""):
        query = self.query or query
        if not query:
            return
        func = getattr(self, f"scrape_{service}_anime_list")
        url = SERVICES["gogo"].format(query=query)
        return func(url)

    def get_download_link(self, url):
        res = requests.get(url, headers=self.headers)
        if res.status_code != 200:
            raise ConnectionError("Your internet might be slow:(")
        tree = html.fromstring(res.text)
        download_link = tree.xpath(".//li[@class='dowloads']//a//@href")[0]
        download_links = self.parse_download_link(download_link)
        return download_links

    def parse_download_link(self, link):
        res = requests.get(link, headers=self.headers)
        tree = html.fromstring(res.text)
        mirrors = tree.xpath("//div[@class='mirror_link']")
        download_opt = []
        for m in mirrors:
            download_opt.append(self.get_mirror(m))
        return download_opt
        
    def get_mirror(self, mirror):
        download_links = mirror.xpath('.//div[@class="dowload"]//a//@href')
        quality = mirror.xpath('.//div[@class="dowload"]//a//text()')
        quality = [self._parse_quality_name(q) for q in quality]
        return dict(zip(quality, download_links))

    def _parse_quality_name(self, text):
        return text.replace("Download", "").replace(" ", "").strip()

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

    def get_episodes(self, tree):
        # res = requests.get(source)
        # tree = html.fromstring(res.text)
        total_episodes = tree.xpath(
            "//ul[@id='episode_page']//li[last()]")[0].text_content().strip().split("-")[-1]
        movie_id = tree.xpath("//input[@id='movie_id']//@value")[0]
        alias_name = tree.xpath("//input[@id='alias_anime']//@value")[0]
        url = self.episode_gateway_url.format(
            total_ep=total_episodes, movie_id=movie_id, alias_name=alias_name)
        return self.get_episodes_parse(url)

    def get_episodes_parse(self, url):
        res = requests.get(url, headers=self.headers)
        if not res.text:
            return []
        tree = html.fromstring(res.text)
        ep_names = [i.strip() for i in tree.xpath(
            "//div[@class='name']/text()[not(parent::span)]")]
        ep_links = [self._refine_url(i.strip())
                    for i in tree.xpath("//a//@href")]
        res = []
        for name, url in zip(ep_names, ep_links):
            d = dict()
            d[name] = url
            res.append(d)
        self.episodes = list(reversed(res))
        return self.episodes

    def get_anime_info_query(self, tree, q):
        xpath = f"//div[@class='anime_info_body_bg']//span[contains(text(), '{q.title()}')]//parent::p//text()[not(parent::span)]"
        data = tree.xpath(xpath)
        return self.clean_data(data)

    def clean_data(self, data):
        if data:
            data = filter(lambda i: i.strip() != '', data)
        return ''.join(data)

    def get_anime_info(self, tree):
        info = ['released', 'plot_summary', 'genre', 'status', 'other_names']
        data = {}
        for i in info:
            data[i] = self.get_anime_info_query(tree, q=i.split('_')[0])
        return data

    def get_popular(self, page=1):
        url = "https://gogoanime.cm/popular.html?page={page}".format(page=page)
        res = requests.get(url, headers=self.headers)
        tree = html.fromstring(res.text)
        items = tree.xpath("//div[@class='last_episodes']//li")
        return self.anime_list_items_parser(items)

    def get_genre_list(self):
        res = requests.get('https://gogoanime.cm', headers=self.headers)
        tree = html.fromstring(res.text)
        nav = tree.xpath("//nav[contains(@class, 'genre')]")[0]
        genre = nav.xpath('.//li//a//text()')
        return genre
    

