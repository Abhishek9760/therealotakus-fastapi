import requests, json
from urllib.parse import urlparse

XSTREAM_CDN_LINK = "https://embedsito.com/api/source/{id}"
def get_links(stream_url):
    id_ = urlparse(stream_url).path.split('/')[-1]
    url = XSTREAM_CDN_LINK.format(id=id_)
    print(url)
    res = requests.post(url,headers={ "referrer": stream_url})
    urls = json.loads(res.text).get('data')
    for i in range(len(urls)):
        url = urls[i]
        link = url.get('file')
        r = requests.get(link, allow_redirects=False, headers={"referrer":"https://embedsito.com/"})
        urls[i]["file"] = r.headers.get('Location')
    return urls