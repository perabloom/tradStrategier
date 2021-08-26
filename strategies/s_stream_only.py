from tia.log import *
import quote as quoteUtil
import trade as tradeUtil
import orders as orderUtil
import positions as position_util
from memoization import cached
import json
import time
import tickprocessor as tickProcessorUtil
import broker as brokerUtil


class STREAM_ONLY:
    def __init__(self, config = {
                    'trade_quantity' : 1,
                    'bar_interval_in_mins' : 0.5,
                    'use_own_date' : False,
                    'is_backtest' : False,
                    'backtest_offset_days' : 0,
                    'max_spread' : 0.10,
                    }):

        self._processor = tickProcessorUtil.TickProcessor(config)
        self._broker = brokerUtil.Broker(self._processor)
        self._config = config
        self.QTY = self._config['trade_quantity']
        self.MAX_SPREAD = self._config['max_spread']



    ASSET_TYPES = ["STOCK"]

    def getProcessor(self):
        return self._processor

    def getBroker(self):
        return self._broker


    def hndl(self, data):
        log().debug(data)
        QTY = self.QTY
        symbol = data[0]['symbol']

        # Process each tick
        for tick in data:
            self._processor.process(symbol, tick)

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
        bid = quote['bid']
        ask = quote['ask']
        if (self._broker.getAC(symbol).BUY_ON_DIFF < (ask - bid)):
            log().warn( symbol + "'s Spread more than BUY_ON_DIFF "  + str(ask - bid) + " , " + str(self._broker.getAC(symbol).BUY_ON_DIFF ))
        tickBars = self._processor.getTickStore(symbol).getTickBars()
        bars = tickBars.getAllBars()
        self._broker.getAC(symbol).hasPosition
        if (len(bars) <= 0):
            return
        if (tickBars.isNewBar()):
            if (False or self._broker.getAC(symbol).hasPosition  or self._broker.getAC(symbol).getRealizedPnL() > 0):
                log().debug(symbol + " Realized : " + str(self._broker.getAC(symbol).getRealizedPnL()))
                log().debug(symbol + " Unrealized : " + str(self._broker.getAC(symbol).getUnrealizedPnL(last)))
                log().debug(symbol + " Position : " + str(self._broker.getAC(symbol).positions))
                log().debug(symbol + " Avg Price : " + str(self._broker.getAC(symbol).cost/max(self._broker.getAC(symbol).positions, 1)))
                log().debug("\n")
            print ("New Bar for ", symbol)
            tickBars.printBars()
            tickBars.plotBars()
            pass
