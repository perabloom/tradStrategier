# Version 3.6.1
from tia.log import *
from datetime import datetime, timedelta

class Bar:
    def __init__(self, o, vol = 0, timesaleType = '', g_h = 0, g_l = 99999):
        self._o = o
        self._h = o
        self._l = o
        self._c = o
        self._vol = vol
        self._vwap = o * vol / max(vol,1)
        self._bearVol = vol if timesaleType == 'BULL' else 0
        self._bullVol = vol if timesaleType == 'BEAR' else 0
        self._g_h = max(o,g_h)  # Running global highest so far
        self._g_l = min(o, g_l) # Running global lowest so far

    def add(self,last, vol = 0, timesaleType = '', g_h = 0, g_l = 99999):
        self._h = max(self._h, last)
        self._l = min(self._l, last)
        self._c = last
        self._vol += vol
        self._vwap = float(( (self._vwap * self._vol) + last * vol)  / max((self._vol + vol), 1))
        self._bearVol += vol if timesaleType == 'BULL' else 0
        self._bullVol += vol if timesaleType == 'BEAR' else 0
        self._g_h = max(last, g_h)  # Running global highest so far
        self._g_l = min(last, g_l) # Running global lowest so far

    def print(self, time = None):
        if (self.isValid()):
            #print ( time, "OHLC : Vol -> ", self._o, ",",self._h,",", self._l,",", self._c, " : ", self._vol)
            # With VWAP
            print ( time, "OHLC : VWAP, Vol -> ", self._o, ",",self._h,",", self._l,",", self._c, " : ",self._vwap, self._vol, self._bearVol, self._bullVol)

    def __str__(self):
          return "OHLC : Vol -> " + str(self._o) + "," + str(self._h) + "," + str(self._l) + "," +  str(self._c) + " : " + str(self._vol)

    def isValid(self):
        if self._o == -1 or self._h == -1:
            return False
        return True

class TickBars:
    # {'bar_interval_in_mins' : 0.5, 'backtest_offset_days' : 0, 'use_own_date' : False}
    def __init__(self, config):
        # in minutes
        self._interval = config['bar_interval_in_mins']
        self._useOwnDate = config['use_own_date']
        self._backTestOffset = config['backtest_offset_days']
        self._isBacktest = False
        log().debug("TickBars config :" + str(config))
        if ('is_backtest' in config):
            log().debug( "IS BACKTEST :" +  str(config['is_backtest']))
            self._isBacktest = config['is_backtest']

        current = datetime.today() - timedelta(days=self._backTestOffset)
        self._market_open = current.replace(hour=9, minute=30, second=0, microsecond=0)
        self._bars = []
        self._newBar = False

    # Adds the price, date, volume and timesaleType BEAR/BULL to the bar.
    # Retruns True only if data is updated False otherwise
    def addToBar(self, price, date, volume = 0, timesaleType = '', g_high = 0, g_low = 9999):
        # for Backtest, always use exchange's timestamp
        if (self._useOwnDate and not self._isBacktest):
            current = datetime.today()
        else:
            current = datetime.fromtimestamp(int(date)/1000)
        delta = current - self._market_open
        if (delta.total_seconds() < 0):
            return False
        minutes = float(delta.total_seconds()/60.0)
        idx = int(divmod(minutes, self._interval)[0])
        while (len(self._bars)< idx):
            if (len(self._bars) <= 0):
                self._bars.append(Bar(-1))
            else:
                self._bars.append(self._bars[-1])
            self._newBar = True
        if (len(self._bars) <= idx):
            self._bars.append(Bar(price, volume, timesaleType,g_high, g_low))
            self._newBar = True
        #print ("IDX : ", idx, " Length : ", len(self._bars))
        else:
            self._bars[idx].add(price, volume, timesaleType, g_high, g_low)
        return True

    def isNewBar(self):
        if (self._newBar == True):
            self._newBar = False
            return True
        return False

    def printBars(self):
        count = 0
        tm = self._market_open
        for bar in self._bars:
            bar.print(tm)
            count += 1
            tm = tm + timedelta(minutes = self._interval)
        #print ("Total Bars : ", count)

    def plotBars(self):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        tm = self._market_open
        t =[]
        o = []
        h =[]
        l = []
        c = []
        vol = []
        vwap = []
        bearVol = []
        bullVol = []
        count = 0
        for bar in self._bars:
            if not bar.isValid():
                tm = tm + timedelta(minutes = self._interval)
                continue
            else:
                t.append(tm)
                tm = tm + timedelta(minutes = self._interval)
            o.append(bar._o)
            h.append(bar._h)
            l.append(bar._l)
            c.append(bar._c)
            vol.append(bar._vol)
            vwap.append(bar._vwap)
            bearVol.append(bar._bearVol)
            bullVol.append(bar._bullVol)

            count += 1
        # Create subplots and mention plot grid size
        fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                    vertical_spacing=0.03, subplot_titles=('OHLC', 'Volume', 'VWAP'),
                    row_width=[0.1, 0.1, 0.2, 0.2, 0.7])
        candlestick = go.Candlestick(x = t, open= o, high = h, low = l, close = c, name = "OHLC")
        fig.add_trace(candlestick, row=1, col=1)
        volume = go.Bar(x=t, y=vol, showlegend=False)
        fig.add_trace(volume, row=2, col=1)
        vwap = go.Scatter(x=t, y=vwap, showlegend=False)
        fig.add_trace(vwap, row=3, col=1)
        bear = go.Bar(x=t, y=bearVol, showlegend=False)
        fig.add_trace(bear, row=4, col=1)
        bull = go.Bar(x=t, y=bullVol, showlegend=False)
        fig.add_trace(bull, row=5, col=1)
        fig.update(layout_xaxis_rangeslider_visible=False)
        #fig = go.Figure(data=[candlestick])
        fig.show()


    def getLastNBars(self,n=3):
        return self._bars[-min(n, len(self._bars)):]

    def getLatestBar(self):
        return self._bars[-1]

    # Deprecated, use getPreviousBar
    def getSecondLastBar(self):
        return self._bars[-2]

    def getPreviousBar(self):
        if (len(self._bars) <2):
            return None
        return self._bars[-2]

    def getAllBars(self):
        return [bar for bar in self._bars if bar.isValid()]


def example():
    a = TickBars({'bar_interval_in_mins' : 0.5, 'backtest_offset_days' : 0, 'use_own_date' : True})
    a.addToBar(45,1626095297000, 23, 'BULL')
    print ("HI")
    a.printBars()
    print ("Getting last n)")
    ln = a.getLastNBars(5)
    for i in ln:
        i.print()

#example()
