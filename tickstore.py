# Version 3.6.1
import quote as quote
import tickbars as tickbars
from tia.log import *

class TickStore:

    def __init__(self, symbol, config):
        log().debug(" Creating Tick Store for " + symbol)
        self._COMMISSION = 0.45
        self._symbol = symbol
        self._stats = quote.getQuote([symbol])[0]
        self._data = {'latest_quote' : self._stats }
        log().debug("TickStore Data " +  str(self._data))

        # Since the quote could be stale, or from earlier day, we should not update it here
        # Furthermore, we want these updated only after market open onwards
        if (True or self._stats['low'] is None):
            self._stats['low'] = 9999999.99
        if (True or self._stats['high'] is None):
            self._stats['high'] = 0.0
        self._stats['is_high_after_low'] = False # False indicates Low is more recent, True indicates High is more recent
        self._tickbars = tickbars.TickBars(config)
        ''' Example
        {'symbol': 'RAPT', 'description': 'RAPT Therapeutics Inc', 'exch': 'Q', 'type': 'stock', 'last': 34.65, 'change': -0.29,
         'volume': 1121021,
         'open': 35.9086, 'high': 35.9086, 'low': 34.32, 'close': 34.65,
         'bid': 34.0, 'ask': 36.95,
         'change_percentage': -0.83, 'average_volume': 101199, 'last_volume': 607338, 'trade_date': 1624651200963, 'prevclose': 34.94,
         'week_52_high': 43.26, 'week_52_low': 14.63,
         'bidsize': 3, 'bidexch': 'Q', 'bid_date': 1624663669000,
         'asksize': 3, 'askexch': 'P', 'ask_date': 1624658403000,
         'root_symbols': 'RAPT'}
        '''
        log().debug(" TickStore INITED for " + symbol)

    def add(self, tick, isOption):
        if (isOption): # FOR OPTION, multiply bid ask prices by 100
            tick['ask'] = float(tick['ask'] )* 100 + self._COMMISSION
            tick['bid'] = float(tick['bid'] ) * 100 - self._COMMISSION
        if (tick['type'] == 'quote'):
            if 'latest_quote' not in self._data or 'bid_date' in self._data['latest_quote']:
                self._data['latest_quote'] = tick
            else:
                if (self._data['latest_quote']['biddate'] <= tick['biddate'] and self._data['latest_quote']['askdate'] <= tick['askdate']):
                    self._data['latest_quote'] = tick
        elif (tick['type'] == 'timesale'):
            tick['last'] = float(tick['last'])
            if (isOption):
                tick['last'] = tick['last'] * 100
            tick['size'] = int(tick['size'])
            tick['date'] = int(tick['date'])
            mid = (float(tick['bid']) + float(tick['ask'])) / 2.0
            timesaleType = ''
            if (tick['last'] > mid):
                timesaleType = 'BULL'
            elif(tick['last'] < mid):
                timesaleType = 'BEAR'
            if 'latest_timesale' not in self._data:
                self._data['latest_timesale'] = tick
            else:
                if (self._data['latest_timesale']['date'] <= tick['date']):
                    self._data['latest_timesale'] = tick
            addedToBar = self._tickbars.addToBar(tick['last'], tick['date'], tick['size'], timesaleType, self._stats['high'], self._stats['low'] )
            if (addedToBar):
                if (tick['last'] < self._stats['low']):
                    self._stats['low'] = tick['last']
                    self._stats['is_high_after_low'] = False
                    log().info(self._symbol + " Lowest updated to " + str(self._stats['low']))
                if (tick['last'] > self._stats['high']):
                    self._stats['high'] = tick['last']
                    self._stats['is_high_after_low'] = True
                    log().info(self._symbol + " Highest updated to " + str(self._stats['high']))


    def getLatestQuote(self):
        if 'latest_quote' not in self._data:
            return None
        return self._data['latest_quote']

    def getLatestTimesale(self):
        if 'latest_timesale' not in self._data:
            return None
        return self._data['latest_timesale']

    def getStats(self):
        return self._stats

    def getTickBars(self):
        return self._tickbars

    def getLowestTick(self):
        return self._stats['low']

    def getHighestTick(self):
        return self._stats['high']

    def getPrevClose(self):
        return self._stats['prevclose']

    # If High is more recent than Low, returns True, False if Low is more recent
    def isHighAfterLow(self):
        return self._stats['is_high_after_low']
