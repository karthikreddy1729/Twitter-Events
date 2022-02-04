

class SubWindow:
    counter = 0
    segment_probabilities = {}
    """
    A subwindow (can be historical or current subwindow), containing:
    - timeframe id
    - dict of segments
    - flag for current/historical timeframe
    - a static dictionary for probabilities
    """

    def __init__(self, segments, tweet_count) -> None:
        self.segments = segments
        self.counter+=1
        self.id = self.counter
        self.tweet_count = tweet_count

    