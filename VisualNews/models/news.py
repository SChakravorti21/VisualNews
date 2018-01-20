import requests, json
from datetime import date
import pymongo

class News(object):

    def __init__(self, title, description, url, date, event=None):
        self.title = title
        self.description = description
        self.url = url
        self.date = date
        self.event = event

    def json(self):
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "date": self.date,
            "event": self.event
        }

    @staticmethod
    def get_news():
        page_size = 100
        page = 1

        url = "https://newsapi.org/v2"

        params = {
            "apikey": "fcf49cf01bcc423bbb85a8473da889cf",
            "from": "2018-01-18T00:00:00-05:00",
            "sources": "abc-news, bloomberg, cbs-news, politico, reuters, the-new-york-times, the-washington-post, nbc-news",
            "pageSize": page_size,
            "page": page,
            "language": "en"
        }

        response = requests.get("{}/everything".format(url), params=params)
        data = json.loads(response.text)
        News.make_news(data['articles'])

        page += 1
        total_pages = int(data['totalResults']) / page_size

        print("{}".format(data['totalResults']))

        while page < total_pages:
            response = requests.get("{}/everything".format(url), params=params)
            data = json.loads(response.text)
            News.make_news(data['articles'])
            page += 1

    @classmethod
    def make_news(cls, articles):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
        db = client['VisualNews']
        collection = db['articles']

        result_articles = []

        for article in articles:
            title = article['title'] if article['title'] is not None else ""
            description = article['description'] if article['description'] is not None else ""
            url = article['url']
            date = article['publishedAt']
            result_articles.append(cls(title, description, url, date))

        for article in result_articles:
            collection.insert_one(article.json())


#News.getNews()
