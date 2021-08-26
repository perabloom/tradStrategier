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

class MOMENTUM_RUN:

    def __init__(self, config = {
                    'trade_quantity' : 1,
                    'bar_interval_in_mins' : 0.25,
                    'use_own_date' : False,
                    'is_backtest' : False,
                    'backtest_offset_days' : 0,
                    'max_spread' : 0.10,
                    }):
        # OVERRIDE VALUES HERE
        config = {
                    'trade_quantity' : 1,
                    'bar_interval_in_mins' : 0.25,
                    'use_own_date' : False,
                    'is_backtest' : False,
                    'backtest_offset_days' : 0,
                    'max_spread' : 0.20,
                    }
        self._processor = tickProcessorUtil.TickProcessor(config)
        self._broker = brokerUtil.Broker()
        self._config = config
        self.QTY = self._config['trade_quantity']
        self.MAX_SPREAD = self._config['max_spread']
        self.MAX_LOSS = 0.05

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
        QTY = self.QTY
        symbol = data[0]['symbol']

        tsTick = None
        # Process each tick
        for tick in data:
            if (tick['type'] == 'timesale'):
                if (tsTick is None):
                    tsTick = tick
            self._processor.process(symbol, tick)

        if (tsTick is None):
            return

        latest_quote = self._processor.getTickStore(symbol).getLatestQuote()
        stats = self._processor.getTickStore(symbol).getStats()
        timesale = self._processor.getTickStore(symbol).getLatestTimesale()
        # if there's no latest trade, return
        if (timesale is None):
            return
        last = timesale['last']
        g_low =  self._processor.getTickStore(symbol).getLowestTick()
        g_high =  self._processor.getTickStore(symbol).getHighestTick()
        prev_close = self._processor.getTickStore(symbol).getPrevClose()
        #print ("Last : ", last, "g_low :", g_low, "High:", g_high, "Prev Close :", prev_close)
        #print(tsTick)
        #print ("Price,Volume : ", tsTick['last'], vol)


        tickBars = self._processor.getTickStore(symbol).getTickBars()
        bars = tickBars.getAllBars()
        if (tickBars.isNewBar()):
            #if (self._broker.getAC(symbol).hasPosition  or self._broker.getAC(symbol).getRealizedPnL() > 0):
            #    print (symbol , "Realized : ", self._broker.getAC(symbol).getRealizedPnL())
            #    print (symbol, "Unrealized : ", self._broker.getAC(symbol).getUnrealizedPnL(last))
            #print ("New Bar for ", symbol)
            #tickBars.printBars()
            #print("\n")
            pass
        dt = datetime.fromtimestamp(int(tsTick['date'])/1000)
        if (self._broker.getAC(symbol).hasPosition is False):
            if (barsUtil.isDownAndNowBetter(bars)):
                print (dt, "isDownAndNowBetter")
                self._broker.buy(symbol, last, self.QTY)
                print("\n")
                tickBars.plotBars()
                #input("Press Enter to continue...")
                #self._processor.getTickStore(symbol).getTickBars().plotBars()
            elif (barsUtil.isUpUpUpUpWithVol(bars)):
                print(dt, "isUpUpUpUpWithVol")
                self._broker.buy(symbol, last, self.QTY)
                print("\n")
                #tickBars.plotBars()
                #input("Press Enter to continue...")
                #self._processor.getTickStore(symbol).getTickBars().plotBars()
        else: # has position
            if (self._broker.getAC(symbol).getUnrealizedPnL(last) < -4.0):
                print (dt, "Unrealized more than 4 dollars, Sell to Close")
                print("REALIZED : ", self._broker.getAC(symbol).getRealizedPnL())
                self._broker.sellToClose(symbol, last)
                print("\n")
                #tickBars.plotBars()
                #input("Press Enter to continue...")
                #self._processor.getTickStore(symbol).getTickBars().plotBars()
            elif (bars[-2]._l > bars[-1]._vwap):
                print (dt, "Current vwap less than lowest of prevous bar, sell now")
                self._broker.sellToClose(symbol, last)
                print("\n")
                #tickBars.plotBars()
                #input("Press Enter to continue...")
            elif (float(self._broker.getAC(symbol).cost/self._broker.getAC(symbol).positions) - last > self.MAX_LOSS):
                print(dt, "loss exceeded ", self.MAX_LOSS)
                self._broker.sellToClose(symbol, last)
                print("\n")
            elif (False and barsUtil.wasUpAndNowFalling(bars)):
                print(dt, "wasUpAndNowFalling")
                #tickBars.printBars()
                #print("REALIZED : ", self._broker.getAC(symbol).getRealizedPnL())
                #self._broker.sellToClose(symbol, last)
                #self._broker.buy(symbol, last, 2 * self._broker.getAC(symbol).positions)
                #tickBars.plotBars()
                #input("Press Enter to continue...")
                print("\n")
                #self._processor.getTickStore(symbol).getTickBars().plotBars()
        if (self._broker.getAC(symbol).getRealizedPnL() < -20):
            print (" realized is less than -20 now : ",self._broker.getAC(symbol).getRealizedPnL())
            exit(0)

''' Asks
1) If for three BARS ( VWAP has been decreasing thrice, buy! now if VWAP so far )
'''
