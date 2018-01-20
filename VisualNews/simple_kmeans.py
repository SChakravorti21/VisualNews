from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.cluster import KMeans, MiniBatchKMeans

import logging
from optparse import OptionParser
import sys
from time import time

import numpy as np

def simple_kmeans(doc_array):
    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    # parse commandline arguments
    op = OptionParser()
    op.add_option("--lsa",
                  dest="n_components", type=int,
                  help="Preprocess documents with latent semantic analysis.")
    op.add_option("--no-minibatch",
                  action="store_false", dest="minibatch", default=True,
                  help="Use ordinary k-means algorithm (in batch mode).")
    op.add_option("--no-idf",
                  action="store_false", dest="use_idf", default=True,
                  help="Disable Inverse Document Frequency feature weighting.")
    op.add_option("--use-hashing",
                  action="store_true", default=False,
                  help="Use a hashing feature vectorizer")
    op.add_option("--n-features", type=int, default=100000,
                  help="Maximum number of features (dimensions)"
                       " to extract from text.")
    op.add_option("--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Print progress reports inside k-means algorithm.")

    print(__doc__)
    op.print_help()
    print()

    def is_interactive():
        return not hasattr(sys.modules['__main__'], '__file__')

    # work-around for Jupyter notebook and IPython console
    argv = [] if is_interactive() else sys.argv[1:]
    (opts, args) = op.parse_args(argv)
    if len(args) > 0:
        op.error("this script takes no arguments.")
        sys.exit(1)

    # #############################################################################
    # Load some data from the training set

    true_k = 30

    print("Extracting features from the training dataset using a sparse vectorizer")
    t0 = time()
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=opts.n_features,
                                     min_df=2, stop_words='english',
                                     use_idf=opts.use_idf)
    X = vectorizer.fit_transform(doc_array)

    print("done in %fs" % (time() - t0))
    print("n_samples: %d, n_features: %d" % X.shape)
    print()


    # #############################################################################
    # Do the actual clustering

    if opts.minibatch:
        km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=opts.verbose,
                             compute_labels=True)
    else:
        km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1,
                    verbose=opts.verbose, compute_labels=True)

    print("Clustering sparse data with %s" % km)
    t0 = time()
    predicted_labels = km.fit_predict(X)
    print("done in %0.3fs" % (time() - t0))
    print()

    if not opts.use_hashing:
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]

        cluster_0 = (np.where(predicted_labels==0))[0]
        X_cluster_0 = X[cluster_0]
        print("X shape: {}".format(X.shape))
        print("X Cluster shape: {}".format(X_cluster_0.shape))
        print(cluster_0)
        print(X_cluster_0)

        articles_at_indices = []
        for i in range(len(cluster_0)):
            if(doc_array[cluster_0[i]] not in articles_at_indices):
                articles_at_indices.append(doc_array[cluster_0[i]])

        import pprint
        pprint.pprint(articles_at_indices)

        # Get the terms in each cluster
        terms = vectorizer.get_feature_names()
        result_labels = []
        for i in range(true_k):
            result_labels.append([])
            # print("Cluster %d:" % i, end='')
            for ind in order_centroids[i, :10]:
                result_labels[i].append(terms[ind])
                # print(' %s' % terms[ind], end='')
        return result_labels


def get_labels():
    from pymongo import MongoClient
    import pprint

    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client['VisualNews']
    collection = db['articles']

    cursor = collection.find({})
    articles = []

    for doc in cursor:
        articles.append(doc['title'] + " -- " + doc['description'])

    results = simple_kmeans(articles)
    # pprint.pprint(results)

get_labels()
