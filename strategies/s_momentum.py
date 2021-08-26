import quote as quoteUtil
import trade as tradeUtil
import orders as orderUtil
import positions as position_util
from memoization import cached
import json
import time
import tickprocessor as tickProcessorUtil
import broker as brokerUtil
import os
import barsUtil

import statistics
from datetime import datetime, timedelta

class MOMENTUM:

    def __init__(self, config = {
                    'trade_quantity' : 100,
                    'bar_interval_in_mins' : 1,
                    'use_own_date' : False,
                    'is_backtest' : False,
                    'backtest_offset_days' : 0,
                    'max_spread' : 0.10,
                    }):
        self._processor = tickProcessorUtil.TickProcessor(config)
        self._broker = brokerUtil.Broker()
        self._config = config
        self.QTY = self._config['trade_quantity']
        self.MAX_SPREAD = self._config['max_spread']

    ASSET_TYPES = ["STOCK"]

    def getProcessor(self):
        return self._processor

    def getBroker(self):
        return self._broker

    def filterOut(self,data):
        if (data['type'] == 'quote'):
            return False
        return False

    def handle(self,data):
        return self.hndl(data)

    def hndl(self,data):
        #print("STRAT_II - ",data)
        QTY = self.QTY
        symbol = data[0]['symbol']

        tsTick = None
        vol = 0
        cnt = 0
        # Process each tick
        for tick in data:
            if (tick['type'] == 'timesale'):
                if (tsTick is None):
                    tsTick = tick
                vol += int(tick['size'])
                cnt += 1
            self._processor.process(symbol, tick)


        if (tsTick is None):
            return
        #print (cnt , "tick processed , representing ", vol, "volume")


        stats = self._processor.getTickStore(symbol).getStats()
        timesale = self._processor.getTickStore(symbol).getLatestTimesale()
        quote = self._processor.getTickStore(symbol).getLatestQuote()
        # if there's no latest trade, return
        if (timesale is None):
            return
        last = timesale['last']
        opn = stats['open']
        g_low =  self._processor.getTickStore(symbol).getLowestTick()
        g_high =  self._processor.getTickStore(symbol).getHighestTick()
        prev_close = self._processor.getTickStore(symbol).getPrevClose()

        tickBars = self._processor.getTickStore(symbol).getTickBars()
        bars = tickBars.getAllBars()
        if (tickBars.isNewBar()):
            #if (self._broker.getAC(symbol).hasPosition  or self._broker.getAC(symbol).getRealizedPnL() > 0):
            #    print (symbol , "Realized : ", self._broker.getAC(symbol).getRealizedPnL())
            #    print (symbol, "Unrealized : ", self._broker.getAC(symbol).getUnrealizedPnL(last))
            #print ("New Bar for ", symbol)
            #tickBars.printBars()
            #tickBars.plotBars()
            print("\n")
            pass

        last_4_highest, last_4_lowest = barsUtil.getHighestAndLowest(bars,15/self._config['bar_interval_in_mins']) # Last 15 minutes
        if (last_4_highest is None or last_4_lowest is None):
            print(last_4_highest, last_4_lowest)
            return
        mid = (last_4_highest + last_4_lowest) / 2.0
        dt = datetime.fromtimestamp(int(timesale['date'])/1000)
        if (self._config['is_backtest']):
            quote['ask'] = last + 0.01
            quote['bid'] = last - 0.01
        if (self._broker.getAC(symbol).hasPosition is False):
            # CHECK IF CURRENT TICK IS BETWEEN HIGHEST AND LOWEST TICK FROM LAST 4 BARS, IF SO, BUY AND SEE WHAT HAPPENS!
            if (last_4_highest - last_4_lowest < 0.10):
                return
            if (abs(last - mid) < 0.01) :
                print (dt, "buying now, tick at ", last, " between : ", last_4_lowest, last_4_highest)
                self._broker.buy(symbol, quote['ask'], self.QTY)
                self._broker.getAC(symbol).MAX_LOSS = abs(last_4_highest - last_4_lowest)/2.0
                self._broker.getAC(symbol).WIN = abs(last_4_highest - last_4_lowest)/2.0
                #tickBars.plotBars()
                print(self._broker.getAC(symbol).WIN, self._broker.getAC(symbol).MAX_LOSS )
                print(self._broker.getAC(symbol).cost/self._broker.getAC(symbol).positions)
                #input("HIVREIT")
        else: # has position
            if (self._broker.getAC(symbol).getUnrealizedPnL(quote['bid']) < -40.0):
                print (dt, "Unrealized more than 4 dollars, Sell to Close")
                print("REALIZED : ", self._broker.getAC(symbol).getRealizedPnL())
                self._broker.sellToClose(symbol, quote['bid'])
            elif (quote['bid'] - self._broker.getAC(symbol).cost/self._broker.getAC(symbol).positions >= self._broker.getAC(symbol).WIN):
                print(dt, "Selling at Profit")
                self._broker.sellToClose(symbol, quote['bid'])
            elif (self._broker.getAC(symbol).cost/self._broker.getAC(symbol).positions - quote['bid'] >= self._broker.getAC(symbol).MAX_LOSS):
                print(dt, "Selling at Loss")
                self._broker.sellToClose(symbol, quote['bid'])

''' Asks
1) If for three BARS ( VWAP has been decreasing thrice, buy! now if VWAP so far )
'''
