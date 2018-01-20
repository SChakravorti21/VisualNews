import twitter, praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

api = twitter.Api(consumer_key="cTSVZ5bCdlVzu0Dd56066KA6R",
                    consumer_secret="rL5HKcf8MjTjXTIxPWjX3byg2xuT2r4BXn62fbdg5kAHITccjw",
                    access_token_key="890539760472739842-7OKzKVW79NCrDyK2YqvJ8Aw1ZcssVaK",
                    access_token_secret="NEwH1FS73oJEG2SNb50sbbbqYRnNVLulJG0g96Aedq2mp")

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

    for submission in news.hot(limit=25):
        
        doc_array = [submission.title, kwd_list]
        similarity = get_text_similarity(doc_array=doc_array)
        if similarity < .1:
            continue
        else:
            print(submission.title)
            multiplier = similarity / 0.1
            comments = submission.comments
            i = 0
            while i < 25 and i < len(comments):
                i += 1
                vs = analyzer.polarity_scores(comments[i].body)
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

#analyze_twitter_sentiment(["government", "shutdown", "Trump", "senate", "budget", "midnight", "crisis", "McConnell", "vote", "funding"])