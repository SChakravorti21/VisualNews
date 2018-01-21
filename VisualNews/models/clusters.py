from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans, MiniBatchKMeans
from VisualNews.sentiment_analysis import get_text_similarity, analyze_twitter_sentiment, analyze_reddit_sentiment

import logging, sys
from optparse import OptionParser
from time import time
import numpy as np
import pprint, json
from datetime import datetime, timedelta
import dateutil.parser as dp

class Cluster():
    def __init__(self, labels=[], articles=[], twitter_sentiment=0.0,
            reddit_sentiment=0.0, cluster_size=0, links=[]):
        self.labels = labels
        self.articles = articles
        self.twitter_sentiment = twitter_sentiment
        self.reddit_sentiment = reddit_sentiment
        self.cluster_size = cluster_size
        self.date = datetime.now()
        self.links = links

    def json(self):
        return {
            "labels": self.labels,
            "articles": self.articles,
            "links": self.links,
            "twitter_sentiment": self.twitter_sentiment,
            "reddit_sentiment": self.reddit_sentiment,
            "cluster_size": self.cluster_size,
            "date": self.date
        }

    def set_twitter_sentiment(self):
        self.twitter_sentiment = analyze_twitter_sentiment(self.labels)

    def set_reddit_sentiment(self):
        self.reddit_sentiment = analyze_reddit_sentiment(self.labels)

    def set_cluster_size(self, docs):
        matches = 0
        words = ' '.join(self.labels)
        print("Words: {}".format(words))
        for article in docs:
            sim = get_text_similarity(doc1=article, doc2=words)
            matches += sim
        self.cluster_size = matches


    @classmethod
    def simple_kmeans(cls, doc_array, true_k=30, n_features=100000, use_idf=True,
                        verbose=False, minibatch=True, use_hashing=False):
        # Create the Vectorizer to turn documents into numeric values
        print(doc_array)
        print("Extracting features from the training dataset using a sparse vectorizer")
        t0 = time()
        vectorizer = TfidfVectorizer(max_df=0.5, max_features=n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=use_idf)
        X = vectorizer.fit_transform(doc_array)

        print("done in %fs" % (time() - t0))
        print("n_samples: %d, n_features: %d" % X.shape)
        print()

        # #############################################################################
        # Do the actual clustering

        if minibatch:
            km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                                 init_size=1000, batch_size=1000, verbose=verbose,
                                 compute_labels=True)
        else:
            km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1,
                        verbose=verbose, compute_labels=True)

        print("Clustering sparse data with %s" % km)
        t0 = time()
        predicted_labels = km.fit_predict(X)
        print("done in %0.3fs" % (time() - t0))
        print()

        if not use_hashing:
            order_centroids = km.cluster_centers_.argsort()[:, ::-1]

            # Aggregate the articles that fall within the same category
            # articles_at_indices is a 2D array, each index holds a 1D array
            # of related documents, corresponding the labels at the same index
            # in result_labels
            clusters = [] # List of Cluster objects to return

            terms = vectorizer.get_feature_names()
            result_labels = []

            articles_at_indices = []
            for k in range(true_k):
                articles_at_indices.append([]) # create new list for next set of articles

                # Get the next cluster
                current_cluster = (np.where(predicted_labels==k))[0]
                # X_cluster = X[cluster]

                for j in range(len(current_cluster)):
                    if(doc_array[current_cluster[j]] not in articles_at_indices[k]):
                        articles_at_indices[k].append(doc_array[current_cluster[j]])

                result_labels.append([])
                for ind in order_centroids[k, :10]:
                    result_labels[k].append(terms[ind])

                # Add the Cluster to the list
                clusters.append(Cluster(labels=result_labels[k], articles=articles_at_indices[k]))

            pprint.pprint(articles_at_indices)

            return clusters

    @staticmethod
    def make_clusters(hour):
        from pymongo import MongoClient

        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client['VisualNews']
        articles_collection = db['articles_{}'.format(hour)]
        clusters_collection = db['clusters_{}'.format(hour)]
        clusters_collection.delete_many({})

        cursor = articles_collection.find({})
        articles = []

        for doc in cursor:
            articles.append(doc['title'] + " –– " + doc['description'])

        # Get the objects of clusters
        results = Cluster.simple_kmeans(articles)
        for cluster in results:
            # Uncomment these once these is the infrastructure to accomodate parsing large datasets
            cluster.set_twitter_sentiment()
            cluster.set_reddit_sentiment()
            t0 = time()
            cluster.set_cluster_size(articles)
            print('Set cluster size in %fs' % (time() - t0))

            # Get the relevant date for the cluster
            t0 = time()
            date = None
            doc_links = []
            for article in cluster.articles:
                split = article.split(' –– ')
                title = split[0]
                description = split[1]
                # print('Title: {}; Description: {}'.format(title, description))
                doc = articles_collection.find_one({'title': title, 'description': description})
                doc_links.append(doc['url'])
                parsed_time = dp.parse(doc['date'])
                in_seconds = parsed_time.strftime('%s')

                if date == None or in_seconds < date:
                    date = in_seconds

            cluster.date = date
            cluster.links = doc_links

            print('Set cluster time in %fs' % (time() - t0))

            pprint.pprint(cluster.json())

            clusters_collection.insert_one(cluster.json())

        pprint.pprint(results[0].json())
