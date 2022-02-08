from itertools import count
from math import exp, sqrt, log10
from scipy.stats import logistic

class TimeWindow:
    """
        Defines current timewindow
        - list of subwindows where all except the last one are historical subwindows
    """
    tweet_count = 0
    unseen_segment_prob = 0.0001

    def __init__(self, _subWindows) -> None:
        self.subWindows = _subWindows
        self.no_subwindows = len(_subWindows)
        self.segments_index = {}
        for subwindow in self.subWindows:
            self.tweet_count += subwindow.tweet_count
    
    def add_subwindow(self, subwindow):
        self.subWindows.append(subwindow)
        self.no_subwindows+=1
        self.tweet_count += subwindow.tweet_count

    def create_prob_dict(self):
        freq_dict = {}
        total_tweet_count = 0
        for sub_window in self.subWindows[:-1]:
            total_tweet_count+=sub_window.tweet_count

            for segment in sub_window.segments.keys():
                if segment not in freq_dict.keys():
                    freq_dict[segment] = 0
                freq_dict[segment] += sub_window.segments[segment].freq
        
        for segment in freq_dict:
            freq_dict[segment] /= total_tweet_count

        self.segment_probabilities = freq_dict

    def get_bursty_segments(self):
        for segment in self.subWindows[-1].segments:
            if segment not in self.segment_probabilities.keys():
                mean = self.unseen_segment_prob * self.tweet_count
                std_dev = sqrt(self.tweet_count * self.unseen_segment_prob * (1 - self.unseen_segment_prob))
            else:
                mean = self.segment_probabilities[segment] * self.tweet_count
                std_dev = sqrt(self.tweet_count * self.segment_probabilities[segment] * (1 - self.segment_probabilities[segment]))
            self.subWindows[-1].segments[segment].burstiness = logistic.cdf((10 * (self.subWindows[-1].segments[segment].freq - mean - std_dev)/(std_dev)))

            print(self.subWindows[-1].segments[segment])