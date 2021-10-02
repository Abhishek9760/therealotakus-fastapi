import requests
from time import sleep
from lxml import html

STREAMSB_DOWNLOAD_LINK = "https://sbplay.org/dl?op=download_orig&id={id}&mode={mode}&hash={hash}"

def get_streamsb(stream_url):
    res = requests.get(stream_url)
    tree = html.fromstring(res.text)
    quality =  tree.xpath("//table//a//text()")
    modes = [i[0].lower() for i in quality]
    img_url = tree.xpath("//img[contains(@alt, 'Download')]//@src")[0]
    id_ = get_streamsbid(img_url)
    hash_ = get_hash(modes[0], "", id_)
    sleep(3)
    return generate_urls(modes, hash_, id_, stream_url, quality)
    
    
def get_streamsbid(img_url):
    url = img_url.split('_')[0]
    return url.split("/")[-1]

def get_hash(mode, hash_, id_):
    download_link = STREAMSB_DOWNLOAD_LINK.format(id=id_, mode=mode, hash=hash_)
    res = requests.get(download_link)
    tree = html.fromstring(res.text)
    hash_ =  tree.xpath("//input[@name='hash']//@value")[0]
    return hash_

def generate_urls(modes, hash_, id_, stream_url, quality):
    urls = {}
    for i in range(len(modes)):
        url = STREAMSB_DOWNLOAD_LINK.format(mode=modes[i], hash=hash_, id=id_)
        urls[quality[i]] = get_download_link(url, stream_url)
    return urls

def get_download_link(url, stream_url):
    res = requests.get(url, headers={"referrer":stream_url})
    tree = html.fromstring(res.text)
    direct_link = tree.xpath("//span//a//@href")[0]
    return direct_link