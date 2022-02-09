from math import exp, sqrt, log10
from scipy.stats import logistic
import numpy as np

class SubWindow:
    counter = 0
    segment_probabilities = {}
    unseen_segment_prob = 0.001
    """
    A subwindow (can be historical or current subwindow), containing:
    - timeframe id
    - dict of segments
    - flag for current/historical timeframe
    - a static dictionary for probabilities
    """

    def __init__(self, segments, tweet_count) -> None:
        self.segments = segments
        SubWindow.counter+=1
        self.id = self.counter
        self.tweet_count = tweet_count

    def __str__(self) -> str:
        return "SubWindow, id: {} tweet count: {}".format(self.id, self.tweet_count)

    def get_bursty_segments(self):
        for segment in self.segments:
            if segment not in self.segment_probabilities.keys():
                mean = SubWindow.unseen_segment_prob * self.tweet_count
                std_dev = sqrt(self.tweet_count * SubWindow.unseen_segment_prob * (1 - SubWindow.unseen_segment_prob))
            else:
                mean = self.segment_probabilities[segment] * self.tweet_count
                std_dev = sqrt(self.tweet_count * self.segment_probabilities[segment] * (1 - self.segment_probabilities[segment]))
            self.segments[segment].burstiness = logistic.cdf((10 * (self.segments[segment].freq - mean - std_dev)/(std_dev)))


    def create_embeddings(self, ngrams = 2):
        for segment in self.segments:
            e = []
            for tweet in self.segments[segment].tweets:
                tweet = tweet.replace(self.segments[segment].segment, "$")
                tokens = tweet.split(" ")
                seg_idx = tokens.index("$")
                l_idx = max(0, seg_idx-ngrams)
                r_idx = min(seg_idx+ngrams, len(tokens)-1)
                # [e.append(context for context in tokens[l_idx:seg_idx]+tokens[seg_idx+1:r_idx+1])]
                e+=tokens[l_idx:seg_idx]
                e+=tokens[seg_idx+1:r_idx+1]
            self.segments[segment].embeddings = e
            print(self.segments[segment]) 
    
    def get_word_embedding_vector(self, segment):
        emb_vec = np.zeros(shape=(len(self.segments)+1, ))
        for embedding in self.segments[segment].embeddings:
            if embedding in self.segments.keys():
                emb_vec[self.segments[embedding].index] += 1
        print(emb_vec)
        return emb_vec

    def get_tweet_vector(self):
        pass

    def get_similarity_matrix(self):
        pass