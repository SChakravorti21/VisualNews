from VisualNews.models.news import News
from VisualNews.models.clusters import Cluster

hour = News.get_news()
Cluster.make_clusters(hour)