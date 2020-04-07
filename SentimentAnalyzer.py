import pandas as pd
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from nltk.tokenize import RegexpTokenizer

'''
Get Data For Classification
'''


class SentimentAnalyze:
    def sentiment(self):
        tweets_data = pd.read_excel('Data/preprocessedTweets.xlsx')
        tokens = tweets_data['text']
        tkr = RegexpTokenizer('[a-zA-Z@]+')

        tweets_split = []

        for i, line in enumerate(tokens):
            tweet = str(line).lower().split()
            tweet = tkr.tokenize(str(tweet))

            tweets_split.append(tweet)

        # Convert words to integers
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(tweets_split)
        data_to_predict = (tokenizer.texts_to_sequences(tweets_split))

        # lenght of tweet to consider
        maxlentweet = 25

        # add padding
        data_to_predict = pad_sequences(data_to_predict, maxlen=maxlentweet)
        model = load_model('models/balanced_model.h5', compile=False)

        # Getting sentiments of obtained data

        Sentiments = model.predict_classes(data_to_predict)
        return Sentiments
