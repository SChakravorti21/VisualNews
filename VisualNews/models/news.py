import requests, json
from datetime import date

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
    def getNews():
        page_size = 100
        page = 1

        url = "https://newsapi.org/v2"

        params = {
            "apikey": "fcf49cf01bcc423bbb85a8473da889cf",
            "from": date.today().isoformat(),
            "sources": "abc-news, bloomberg, cbs-news, politico, reuters, the-new-york-times, the-washington-post, nbc-news",
            "pageSize": page_size,
            "page": page
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
        articles = []

        for article in articles:
            title = article['title']
            description = article['description']
            url = article['url']
            date = article['publishedAt']
            articles.append(cls(title, description, url, date))
        
        print("success")


News.getNews()