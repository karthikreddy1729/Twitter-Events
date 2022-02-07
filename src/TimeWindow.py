



class TimeWindow:
    """
        Defines current timewindow
        - list of subwindows where all except the last one are historical subwindows
    """
    def __init__(self, _subWindows) -> None:
        self.subWindows = _subWindows
        self.no_subwindows = len(_subWindows)
        self.segments_index = {}
    
    def add_subwindow(self, subwindow):
        self.subWindows.append(subwindow)
        self.no_subwindows+=1