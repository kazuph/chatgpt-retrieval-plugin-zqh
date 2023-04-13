from datetime import datetime

import pytz
import httpx
from bs4 import BeautifulSoup

from models.models import Source

PLUGIN_HOST = 'http://localhost:3333'

sites = [
    # (Source.qiita, 'https://b.hatena.ne.jp/site/qiita.com'),
    # (Source.zenn, 'https://b.hatena.ne.jp/site/zenn.dev'),
    # テクノロジー - プログラミング
    (Source.hatena, 'https://b.hatena.ne.jp/entrylist/it/%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0'),
]

def fetch_and_upsert(site):
    (source, feed_url) = site

    for page in range(1, 50):
        url = f'{feed_url}?page={page}&sort=recent&threshold=3&mode=text'
        print(f"fetching {url}")
        soup = BeautifulSoup(httpx.get(url).text, 'html.parser')
        entrylist = soup.select('div.entrylist-contents-main')
        documents = []
        for item in entrylist:
            link = item.h3.a['href']
            title = item.h3.a.text
            summary = item.div.text.strip()
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

        print(f"upserting {len(documents)} documents...")
        result = httpx.post(f'{PLUGIN_HOST}/upsert', timeout=600, json={
            'documents': documents
        })
        print(f"done: {result.status_code}")


if __name__ == '__main__':
    for site in sites:
        fetch_and_upsert(site)