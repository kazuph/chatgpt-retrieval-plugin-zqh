import httpx
from bs4 import BeautifulSoup
from unstructured.partition.html import partition_html

from models.models import Source

PLUGIN_HOST = 'http://localhost:3333'

sites = [
    (Source.qiita, 'https://b.hatena.ne.jp/site/qiita.com'),
    (Source.zenn, 'https://b.hatena.ne.jp/site/zenn.dev'),
    (Source.hatena, 'https://b.hatena.ne.jp/entrylist/it/%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0'), # テクノロジー - プログラミング
]

def fetch_and_upsert(site, pages=50, offset=1):
    (source, feed_url) = site

    for page in range(offset, pages+1):
        url = f'{feed_url}?page={page}&sort=recent&threshold=3&mode=text'
        print(f"fetching {url}")
        soup = BeautifulSoup(httpx.get(url).text, 'html.parser')
        entrylist = soup.select('div.entrylist-contents-main')
        documents = []
        for item in entrylist:
            title = item.h3.a.text
            link = item.h3.a['href']
            try:
                elements = partition_html(url=link)
                summary = "\n\n".join([str(el) for el in elements])
                date_str = item.select_one('li.entrylist-contents-date').text
                doc = {
                    'id': link,
                    'text': title + "\n" + summary,
                    'metadata': {
                        'title': title,
                        'source': source,
                        'url': link,
                        'created_at': date_str+':00+0900',
                    }
                }
                documents.append(doc)
            except ValueError as e:
                print(f"error: {e}. link: {link}")
                continue

        print(f"upserting {len(documents)} documents...")
        result = httpx.post(f'{PLUGIN_HOST}/upsert', timeout=600, json={
            'documents': documents
        })
        print(f"done: {result.status_code}")


if __name__ == '__main__':
    for site in sites:
        fetch_and_upsert(site, pages=10)