import feedparser

from models.models import QueryResult, DocumentChunkWithScore, Source

def search_hatena_bookmark(keywords, users=3, sort="recent", target="all"):
    query_string = f"users={users}&sort={sort}&mode=rss&target={target}"
    url = f"https://b.hatena.ne.jp/q/{keywords}?{query_string}"
    feed = feedparser.parse(url)
    docs = []
    for entry in feed.entries:
        doc = DocumentChunkWithScore(id=entry.link,
                                     text=entry.title + "\n" + entry.summary,
                                     metadata={
                                         'title': entry.title,
                                         'source': Source.hatena,
                                         'url': entry.link,
                                         'created_at': entry.updated,
                                     },
                                     score=float(entry.hatena_bookmarkcount))
        docs.append(doc)

    return [QueryResult(query=keywords, results=docs)]
