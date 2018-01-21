import twitter, praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

api = twitter.Api(consumer_key="KNMAMu8mH1EufzO2pwD7Erhkd",
                    consumer_secret="SKkCvIpVpuSBpyX0jwhRCBAffyqturk2OUFIvYKZL49wonf9LK",
                    access_token_key="2675842215-wx3eCPrPahmVlJIeticgmuUTVEtInvE9oRee5QM",
                    access_token_secret="GVN0k87OQvgGQwPVbLNsXbqX779FlhVKJU5H5vD51DWSF")

reddit = praw.Reddit(client_id='fXu6e5Ofuroemg',
                     client_secret='lEX8uGB1KHR3peMRql9BUHw9sKY',
                     password='tdE-DQG-Pe2-bLZ',
                     user_agent='sentimentbot for newsvisualizer',
                     username='articlesentimentbot')
news = reddit.subreddit('news')

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

    for kwd in kwds:
        kwd_list = kwd_list + "{} ".format(kwd)

    queries = make_twitter_queries(kwds)
    for query in queries:
        results = api.GetSearch(raw_query=query)
        for result in results:
            tweets.append(result.text)

    count = 0.0
    total = 0.0
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

def make_twitter_queries(kwds):
    base_query = "l=en&q="
    queries = []

    i = 0
    while i < 10:
        query = base_query + "{}%20OR%20{}&count=100".format(kwds[i], kwds[i+1])
                #kwds[i+2], kwds[i+3], kwds[i+4])
        queries.append(query)
        i += 2

    return queries

def analyze_reddit_sentiment(kwds):
    kwd_list = ""

    count = 0.0
    total = 0.0
    multiplier = 1.0

    for kwd in kwds:
        kwd_list = kwd_list + "{} ".format(kwd)

    for submission in news.hot(limit=50):

        doc_array = [submission.title, kwd_list]
        similarity = get_text_similarity(doc_array=doc_array)
        if similarity < .05:
            continue
        else:
            from praw.models import MoreComments
            print(submission.title)
            multiplier = similarity / 0.1
            comments = submission.comments
            #comments.replace_more(limit=None)
            i = 0
            for comment in comments:
                if i >= 25 or i >= len(comments.list()):
                    break
            # for i in range(len(comments)):
                i += 1
                if isinstance(comment, MoreComments):
                    continue
                vs = analyzer.polarity_scores(comment.body)
                if vs['compound'] == 0.0:
                    continue
                total += vs['compound'] * multiplier
                count += 1

    if total == 0.0:
        print("none")
        return None
    else:
        print(float(total / count))
        return float(total / count)

#analyze_reddit_sentiment(["government", "shutdown", "Trump", "senate", "budget", "midnight", "crisis", "McConnell", "vote", "funding"])
