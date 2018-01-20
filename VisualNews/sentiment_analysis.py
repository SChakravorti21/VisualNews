import twitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

api = twitter.Api(consumer_key="Ld3CmGVdyVLPL6gbzZHv5lxhN",
                    consumer_secret="T4q1RbVjosngsi3WMJxuqCQC66HKvlRdh4J2G5qiH1jMtJsEIq",
                    access_token_key="954621614922125312-yAn0jF9zTLmflhoADnrOj01wA9VhM1o",
                    access_token_secret="HY4XvWJ6uKKEOMeuWYohemVSIqPpKAuJcz83HsBv2huVg")

analyzer = SentimentIntensityAnalyzer()

def get_text_similarity(doc_array=None, doc1="", doc2=""):
    
    res = None
    vect = TfidfVectorizer(stop_words="english")

    if doc_array:
        tfidf = vect.fit_transform([doc for doc in doc_array])
    else:
        tfidf = vect.fit_transform([doc1, doc2])

    res = (tfidf * tfidf.T).toarray()

    return res[0][1]

def analyze_twitter_sentiment(kwds):

    kwd_list = ""
    query = "l=en&q="
    for kwd in kwds:
        kwd_list = kwd_list + "{} ".format(kwd)
        query = query + "{}%20OR%20".format(kwd)

    query = query + "&count=100"
    print(query)

    tweets = api.GetSearch(raw_query=query)
    count = 0
    total = 0

    for tweet in tweets:
        doc_array = [tweet.text, kwd_list]
        if get_text_similarity(doc_array=doc_array) < 0.1:
            continue
        vs = analyzer.polarity_scores(tweet.text)
        if vs['compound'] == 0.0:
            continue
        total = total + vs['compound']
        count += 1

    return float(total / count)

analyze_twitter_sentiment(["government", "news", "trump", "19", "shutdown", "cbs", "senate", "vote", "majority", "president"])