from sklearn.feature_extraction.text import TfidfVectorizer

def get_text_similarity(doc_array=None, doc1="", doc2=""):

    res = None
    vect = TfidfVectorizer(stop_words="english")

    if doc_array:
        tfidf = vect.fit_transform([doc for doc in doc_array])
    else:
        tfidf = vect.fit_transform([doc1, doc2])

    res = (tfidf * tfidf.T).toarray()

    return res

# testing how/whether this works at all
if __name__ == "__main__":
    vect = TfidfVectorizer(stop_words="english")
    doc_array = ["I'd like an apple",
                 "An apple a day keeps the doctor away",
                 "Never compare an apple to an orange",
                 "I prefer scikit-learn to Orange"]
    tfidf = vect.fit_transform(doc_array)

    res = (tfidf * tfidf.T).toarray()
    print(res[0][1])

    print(get_text_similarity(doc_array=doc_array))
