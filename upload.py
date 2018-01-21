from apscheduler.schedulers.blocking import BlockingScheduler

from VisualNews.models.news import News
from VisualNews.models.clusters import Cluster

def load_data():
    print("Running")
    hour = News.get_news()
    Cluster.make_clusters(hour)

def test():
    print("Running")

# Since scheduler will start next job in an hour, start the initial job now
load_data()

scheduler = BlockingScheduler()
# scheduler.add_job(test, 'interval', seconds=1)
scheduler.add_job(load_data, 'interval', hours=1)
scheduler.start()
