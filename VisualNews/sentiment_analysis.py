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
    tweets =[]

    kwd_list = ""
    base_query = "l=en&q="
    for kwd in kwds:
        kwd_list = kwd_list + "{} ".format(kwd)
        query = base_query + "{}&count=100".format(kwd)
        print(query)
        results = api.GetSearch(raw_query=query)
        for result in results:
            tweets.append(result.text)

    count = 0
    total = 0
    multiplier = 1.0

    for tweet in tweets:
        doc_array = [tweet, kwd_list]

        similarity = get_text_similarity(doc_array=doc_array)

        if similarity < 0.1:
            continue

        multiplier = similarity / 0.1
        vs = analyzer.polarity_scores(tweet)

        if vs['compound'] == 0.0:
            continue

        total = total + vs['compound'] * multiplier
        count += 1

    print("{} / {} = {}".format(total, count, float(total / count)))
    return float(total / count)

#analyze_twitter_sentiment(["government", "news", "trump", "death", "shutdown", "senate", "vote", "majority", "North Korea"])