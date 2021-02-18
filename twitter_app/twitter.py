"""Prediction of Users based on Tweet Embeddings"""
import numpy as np
from sklearn.linear_model import LogisticRegression
import spacy  # Vectorizes our tweets


from .models import User

try:
    nlp = spacy.load('en_core_web_sm')
except:
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector


def predict_user(user0, user1, tweet_text):
    
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # vertically stack embedddings to create one list of vects
    X = np.vstack([user0_vects, user1_vects])  # user0_vects on user1_vects

    # collection of labels same length as vects
    y = np.concatenate([np.zeros(len(user0.tweets)), np.ones(len(user1.tweets))])  # 0 is user0, 1 is user1

    # creating logistic regression model and fitting
    model = LogisticRegression()
    model.fit(X, y)

    # converting tweet text to vector
    tweet_vect = vectorize_tweet(tweet_text)

    # formats hypo_tweet_vect and runs prediction, will return 0 or 1
    return model.predict([tweet_vect])
