import requests
from lxml import html

STREAMSB_DOWNLOAD_LINK = "https://sbplay.org/dl?op=download_orig&id={id}&mode={mode}&hash={hash}"

def get_streamsb(stream_url):
    res = requests.get(stream_url)
    tree = html.fromstring(res.text)
    modes = [i[0].lower() for i in tree.xpath("//table//a//text()")]
    img_url = tree.xpath("//img[contains(@alt, 'Download')]//@src")[0]
    id_ = get_streamsbid(img_url)
    hash_ = get_hash(modes[0], "", id_)
    return generate_urls(modes, hash_, id_)
    
    
def get_streamsbid(img_url):
    url = img_url.split('_')[0]
    return url.split("/")[-1]

def get_hash(mode, hash_, id_):
    download_link = STREAMSB_DOWNLOAD_LINK.format(id=id_, mode=mode, hash=hash_)
    res = requests.get(download_link)
    tree = html.fromstring(res.text)
    hash_ =  tree.xpath("//input[@name='hash']//@value")[0]
    return hash_

def generate_urls(modes, hash_, id_):
    urls = []
    for mode in modes:
        url = STREAMSB_DOWNLOAD_LINK.format(mode=mode, hash=hash_, id=id_)
        res = requests.get(url)
        tree = html.fromstring(res.text)
        direct_link = tree.xpath("//span[contains(@style,'background')]//a//@href")
        if len(direct_link) > 0:
            direct_link = direct_link[0]
        urls.append(direct_link)
    return urls