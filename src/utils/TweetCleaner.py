import os
import pandas as pd
import json
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from ekphrasis.classes.segmenter import Segmenter
nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')
import preprocessor as p


class TweetCleaner:
    """
    cleaning steps:
    - remove hashtags, punctuations, stopwords, hyperlinks, emojis
    - lemmatize
    - tokenize
    """
    lemmatizer = WordNetLemmatizer()                #per word
    tokenizer = TweetTokenizer()                    #per sentence
    stop_words = set(stopwords.words('english'))
    # seg = Segmenter(corpus='twitter')

    def __init__(self, remove_retweets=True) -> None:
        self.remove_retweets = remove_retweets

    def get_cleaned_text(self, text):
        """
        removes punctuations, hashtags, emojis, mentions, reserved words
        """
        cleaned_text = p.clean(text)
        cleaned_text = [self.lemmatizer.lemmatize(word) for word in self.tokenizer.tokenize(cleaned_text)]
        cleaned_text = ' '.join(token for token in cleaned_text if len(token)>1)
        return cleaned_text

    def clean(self, filename):
        fp = open(filename)
        file_json = json.load(fp)
        op_dict = []
        for tweet in file_json:
            if 'retweeted_status' in tweet.keys():
                if self.remove_retweets: continue
            if "lang" in tweet.keys() and tweet["lang"] != "eng": continue
            cleaned_text = self.get_cleaned_text(tweet["text"])
            cleaned_tweet = {}
            cleaned_tweet["created_at"] = tweet["created_at"]
            cleaned_tweet["id"] = tweet["id"]
            cleaned_tweet["text"] = cleaned_text
            cleaned_tweet["user"]["id"] = tweet["user"]["id"]
            cleaned_tweet["retweet_count"] = tweet["retweet_count"]
            op_dict.append(cleaned_tweet)
        with open("{}_cleaned.json".format(filename[:-5]), 'w') as op_fp:
            json.dump(op_dict, op_fp)
        

cleaner = TweetCleaner()
cleaner.clean('../Data/unprocessed_data/sample.json')