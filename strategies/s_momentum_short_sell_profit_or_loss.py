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
import os
import barsUtil
from datetime import datetime

import statistics
from datetime import datetime, timedelta
from abstractStrategy import ABSTRACT_STRATEGY


class STATE:
    NONE = "NONE" # Corresponds to s_market_make
    PROFIT_1ST_BUY = "PROFIT_1ST_BUY"
    PROFIT_2ND_BUY = "PROFIT_2ND_BUY"
    THIRD_BUY_ON_PRICE_DROP = "THIRD_BUY_ON_PRICE_DROP"
    UNSCATHED = "UNSCATHED" # Indicates last was coming out unscathed
    ACTIVE = "ACTIVE"
    PROFITS_IN_ONE_BUY = "PROFITS_IN_ONE_BUY"
    PROFITS_IN_TWO_BUYS = "PROFITS_IN_TWO_BUYS"
    PROFIT_POST_MULTIPLE_BUYS = "PROFIT_POST_MULTIPLE_BUYS"


class MOMENTUM_SHORT_SELL_PROFIT_OR_LOSS(ABSTRACT_STRATEGY):

    def __init__(self, config = None):
        is_backTest = False
        backtest_offset_days = 0
        bar_interval = 0.5
        if (config is not None):
            is_backTest = config['is_backtest']
            backtest_offset_days = config['backtest_offset_days']
            bar_interval = config['bar_interval_in_mins']
        # Now overwrite the config if it's is backtest
        config = {
            'trade_quantity' : 10,
            'bar_interval_in_mins' : bar_interval,
            'use_own_date' : False,
            'is_backtest' : is_backTest,
            'backtest_offset_days' : backtest_offset_days,
            'max_spread' : 0.10,
            }
        self._processor = tickProcessorUtil.TickProcessor(config)
        self._broker = brokerUtil.Broker(self._processor)
        self._config = config
        self.QTY = self._config['trade_quantity']
        self.MAX_SPREAD = self._config['max_spread']
        self.CAPITAL = 600
        self.MARKET_OPENED = False
        self.lastLimitUpdatetime_for_backtest = None
        self.profitMap = {}
        self.DIFF = 0.10

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
        log().debug(data)
        QTY = self.QTY
        symbol = data[0]['symbol']
        isOption = False
        if (len(symbol) > 13):
            isOption = True

        # Process each tick
        for tick in data:
            self._processor.process(symbol, tick, isOption)


        stats = self._processor.getTickStore(symbol).getStats()
        timesale = self._processor.getTickStore(symbol).getLatestTimesale()
        quote = self._processor.getTickStore(symbol).getLatestQuote()
        #print(quote)
        # Check if market is open or NOT
        if (self.MARKET_OPENED is False):
            if (self._config['is_backtest']):
                current = datetime.today() - timedelta(days=self._config['backtest_offset_days'])
            else:
                current = datetime.today()
            market_open_time = current.replace(hour=9, minute=30, second=0, microsecond=0)

            if (timesale is not None):
                tick_date = timesale['date']
            else:
                tick_date = max(quote['biddate'], quote['askdate'])

            tick_time = datetime.fromtimestamp(int(tick_date)/1000)
            #print(tick_time, market_open_time)
            if ( tick_time > market_open_time):
                # SET THAT MARKET IS OPEN
                self.MARKET_OPENED = True
            else:
                # MARKET IS NOT OPEN YET
                return

        opn = stats['open']
        g_low =  self._processor.getTickStore(symbol).getLowestTick()
        g_high =  self._processor.getTickStore(symbol).getHighestTick()
        is_high_after_low = self._processor.getTickStore(symbol).isHighAfterLow() # if tr
        prev_close = self._processor.getTickStore(symbol).getPrevClose()

        if (self._config['is_backtest']):
            # if there's no latest trade, return
            if (timesale is None):
                return
            last = timesale['last']
            quote['ask'] = last + 0.01
            quote['bid'] = last - 0.01

        bid = quote['bid']
        ask = quote['ask']

        ac = self._broker.getAC(symbol)

        # THIS INDICATES DO NOT TRADE IN THIS STOCK
        if (ac.stopTrading):
            return

        #if (self._broker.getAC(symbol).BUY_ON_DIFF < (ask - bid)):
        #    log().warn( symbol + "'s Spread more than BUY_ON_DIFF "  + str(ask - bid) + " , " + str(self._broker.getAC(symbol).BUY_ON_DIFF ))
        # IF SPREAD IS GREATER THAN 2 cents, just Don't TRADE if there's NO positions already !
        SPREAD_DELTA = 0.021
        if (isOption):
            SPREAD_DELTA = SPREAD_DELTA * 100
        if (SPREAD_DELTA <= (ask - bid) and ac.hasPosition == False):
            return

        tickBars = self._processor.getTickStore(symbol).getTickBars()
        bars = tickBars.getAllBars()


        if (timesale is not None):
            tick_date = timesale['date']
        else:
            tick_date = max(quote['biddate'], quote['askdate'])

        dt = datetime.fromtimestamp(int(tick_date)/1000)
        dt = dt.replace(microsecond=1000*(int(tick_date)%1000))
        dt = dt.strftime("%H:%M:%S.%f")
        now = datetime.now()
        dt = dt + " " + now.strftime("%H:%M:%S.%f")
        dt = dt + " " + symbol + " ACTION "

        #if (self._broker.getAC(symbol).BUY_ON_DIFF < (ask - bid)):
        #    log().warn(dt + " Spread more than BUY_ON_DIFF "  + str(ask - bid) + " , " + str(self._broker.getAC(symbol).BUY_ON_DIFF ))

        if (ac.checkAndResetBuyFlag()):
            log().info(dt + " BUY_FLAG_ENABLED Buy ")
            self._broker.buyToCover(symbol, quote['ask'])
            self.profitMap[symbol]['maxProfit'] = 0
            return

        if (ac.checkAndResetSellAllFlag()):
            log().info(dt + " SELL_SHORT_FLAG_ENABLED Sell SHORT ")
            self._broker.sellShort(symbol, quote['bid'], int(self.CAPITAL/quote['bid']))
            self.profitMap[symbol]['maxProfit'] = 0
            return

        if (ac.hasPosition is False):
            return
            if (ac.NUM_BUY_SELL_LOOPS == 0 and ac.NUM_UNCLOSED_BUY_TXNS  == 0):
                log().info(dt + " SELL_SHORT_AT_OPEN " + str(int(self.CAPITAL/quote['bid'])) + "@" + str(quote['bid']))
                self._broker.sellShort(symbol, quote['bid'], int(self.CAPITAL/quote['bid']) )
        else: # has position
            # Make these dependent on positions
            avg_price = self._broker.getAC(symbol).cost/self._broker.getAC(symbol).positions
            quantity = int(self._broker.getAC(symbol).positions)
            if (symbol not in self.profitMap):
                self.profitMap[symbol] = {'maxProfit' : 0}
            self.profitMap[symbol]['maxProfit'] = max((quote['ask'] - avg_price) * (ac.positions), self.profitMap[symbol]['maxProfit'])
            log().debug("HAVE POSITION : " + str(data))
            # CHECK IF WE ALREADY ACHIEVED OUR 🎯
            if ( avg_price - quote['ask'] >= ac.DAILY_MAX_PCT_CHANGE * avg_price / 2  ):
                if ( (quote['ask'] - avg_price) * (ac.positions) < self.profitMap[symbol]['maxProfit'] ):
                    log().info(dt + " BUYING_TO_COVER_AS_TARGET_ACHIEVED Selling at Profit, Target achieved" + str(ac.positions) + "@" + str(quote['ask']))
                    self._broker.buyToCover(symbol, quote['ask'])
                    self.profitMap[symbol]['maxProfit'] = 0
            # THINK WHAT WE WANT TO DO NOW!!?!?
            # PERHAPS THINK ABOUT INCORPORATING WHAT"s THE MAX CAPITAL WE ARE PUTTING IN
            elif ( quote['ask'] - avg_price >= ac.DAILY_MAX_PCT_CHANGE * avg_price):
                log().info(dt + " BUYING_TO_COVER_AT_A_LOSS " + str(ac.positions) + "@" + str(quote['ask']))
                self._broker.buyToCover(symbol, quote['ask'])
                self.profitMap[symbol]['maxProfit'] = 0


    def getStrategy(self, symbol = None):
        symbolMap = self._broker.getSymbolMap()
        for sym, ac in symbolMap.items():
            if (symbol is not None):
                if (symbol != sym):
                    continue
            if (ac.hasPosition == False):
                continue

'''
# TODOS
# REFACTOR THE STRATEGY CONSTRUCTOR TO TAKE IN SYMBOLS!
'''
