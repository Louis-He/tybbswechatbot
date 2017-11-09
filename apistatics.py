class statics:
    #initialize statistic
    def __init__(self):
        self.minutetime = []
        self.minuterstatistic = []

    def update(self, ts, browse):
        # save 72-hr minutes data
        if len(self.minutetime) >= 4320:
            self.minutetime.remove(self.minutetime[0])
            self.minuterstatistic.remove(self.minuterstatistic[0])

        self.minutetime.append(ts)
        self.minuterstatistic.append(browse)

    def getbrowse(self, period):
        length = len(self.minutetime)
        result = 0
        if length < period:
            return "ERR: INSUFFICIENT data to display " + period + "seconds browse history"
        else:
            for i in range(period, 0, -1):
                result += self.minutetime[length - i]
            return result

def clearstatistic():
    return 0