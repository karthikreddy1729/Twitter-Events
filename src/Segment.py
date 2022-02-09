import json
import re
from SubWindow import SubWindow
from TimeWindow import TimeWindow

def split_hashtag(hashtag):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', compound_word)
    return ' '.join([m.group(0) for m in matches]).lower()

class Segment:
    counter = 0
    def __init__(self,segment):
        """
        segment           - string of words ex. 'steve jobs'
        """
        self.segment = segment
        Segment.counter+=1
        self.index = self.counter
        self.tweets = []            # list of tweets( text:str ) containing this segment in current time window
        
        self.freq = 0               # tweet-freq i.e. number of tweets containing this segment
        self.user_set = set()       # no. of unique users that used this segment in current time window
        self.retweet_count = 0      # sum of retweet counts of all tweets containing this segment
        # self.followers_count = 0    # sum of followers count of all users using this segment
        self.burstiness = 0     # measure of importance of segment calculated by Twevent's Q(s) values
        self.embeddings = []
        

    def __str__(self):
        # return 'Segment:'+self.segment+', freq:'+str(self.freq)+', user_count:'+str(self.get_user_count())   
        return "Segment Index: {}, Segment: {}, freq: {}, burstiness: {}, user_count: {} \n embeddings: {}\n".format(self.index, self.segment, self.freq, self.burstiness, self.user_set, self.embeddings)
        
    def add_tweet(self, user_id, text, retweet_count):    
        self.user_set.add(user_id)
        if text not in self.tweets:
            self.tweets.append(text)
            self.freq += 1
        self.retweet_count += retweet_count
        # self.followers_count += followers_count
        
    def get_user_count(self):
        return len(self.user_set)


class TimeframeTweetSegmentor:
    """
    creates a sub windows for the timeframe.
    wikipedia titles file: '../Data/enwiki-titles-unstemmed/enwiki-titles-unstemmed.txt'
    """
    TimeWindow = TimeWindow([])
    def __init__(self, wikipedia_titles_file, seg_len, hashtag_weight) -> None:
        self.seg_len = seg_len
        self.hashtag_wt = hashtag_weight
        
        wikipedia_titles = {}       # 2 level dict, 1st level is 'a' to 'z' and 'other' to make search faster!!
        for i in range(97,123):
            wikipedia_titles[chr(i)] = set()
        wikipedia_titles['other']= set()

        f = open(wikipedia_titles_file, 'r')
        for title in f:
            title = title.replace('\n','')
            index = ord(title[0])
            if index in range(97,123): wikipedia_titles[chr(index)].add(title)
            else: wikipedia_titles['other'].add(title)    
                    
        self.wikipedia_titles = wikipedia_titles
    
    def is_title_present(self, title):
        """
        check if given title(string) is in wiki_titles
        """
        index = ord(title[0])
        if index in range(97,123): return title in self.wikipedia_titles[chr(index)]
        else: return title in self.wikipedia_titles['other']  

    def segment_tweets(self, ip_file):
        f = open(ip_file)
        tweets_json = json.load(f)
        segments_dict = {}
        for tweet in tweets_json:
            text = tweet["text"]
            tokens = text.split(" ")
            word_count = len(tokens)
            segments = []
            i = 0
            while i < word_count:
                j = min(i + self.seg_len, word_count) # check if tokens[i:j] is a title otherwise decrease j
                while True:
                    seg = ' '.join(tokens[i:j])
                    if self.is_title_present(seg):
                        segments.append(seg)
                        if seg not in segments_dict.keys():
                            segments_dict[seg] = Segment(seg)
                        segments_dict[seg].add_tweet(tweet["user"]["id"], tweet["text"], tweet["retweet_count"])
                        i = j
                        break
                    elif j == i+1: # one word
                        segments.append(tokens[i])
                        if tokens[i] not in segments_dict.keys():
                            segments_dict[tokens[i]] = Segment(tokens[i])
                        segments_dict[tokens[i]].add_tweet(tweet["user"]["id"], tweet["text"], tweet["retweet_count"])
                        i += 1
                        break
                    else:
                        j -= 1

                segments = [s for s in segments if len(s)>2]

                for hashtag in tweet["entities"]["hashtags"]:
                    hashtag = re.sub('[0-9]+','',hashtag)
                    hashtag = ' '.join([self.compound_word_split(i) for i in hashtag.split('_') if len(i)>0])
                    if len(hashtag)>2:
                        segments += [hashtag] * self.hashtag_wt
        return segments_dict, len(tweets_json)

    def create_subwindows(self, file_list):
        for file_name in file_list:
            segments, tweet_count = self.segment_tweets(file_name)
            sub_win = SubWindow(segments, tweet_count)
            print(sub_win)
            self.TimeWindow.add_subwindow(sub_win)

tf = TimeframeTweetSegmentor('../Data/enwiki-titles-unstemmed/enwiki-titles-unstemmed.txt', 3, 2)
tf.create_subwindows(['../Data/unprocessed_data/sample.json'])
tf.TimeWindow.create_prob_dict()
tf.TimeWindow.subWindows[-1].get_bursty_segments()
tf.TimeWindow.subWindows[-1].create_embeddings()
tf.TimeWindow.subWindows[-1].get_word_embedding_vector("ottimes")