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
    NONE = "INIT" # Corresponds to s_market_make
    PROFIT_1ST_BUY = "PROFIT_1ST_BUY"


class MOMENTUM_BUY_MORE(ABSTRACT_STRATEGY):

    def __init__(self, config = None):
        is_backTest = False
        backtest_offset_days = 0
        if (config is not None):
            is_backTest = config['is_backtest']
            backtest_offset_days = config['backtest_offset_days']
        # Now overwrite the config if it's is backtest
        config = {
            'trade_quantity' : 10,
            'bar_interval_in_mins' : 0.5,
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
        self.CAPITAL = 1000
        self.MARKET_OPENED = False
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
        #log().debug(data)
        QTY = self.QTY
        symbol = data[0]['symbol']
        isOption = False
        # Check if option or not
        if (len(symbol) > 13):
            isOption = True

        # Process each tick
        for tick in data:
            self._processor.process(symbol, tick, isOption)

        timesale = self._processor.getTickStore(symbol).getLatestTimesale()
        quote = self._processor.getTickStore(symbol).getLatestQuote()

        # Check if market is open or NOT
        if (self.MARKET_OPENED is False):
            if (self._config['is_backtest']):
                current = datetime.today() - timedelta(days=self._config['backtest_offset_days'])
            else:
                current = datetime.today()
            market_open_time = current.replace(hour=9, minute=30, second=0, microsecond=0)

            # This is primarily for detrmining the open! ( and as well for logging purpose)
            if (timesale is not None):
                tick_date = timesale['date']
            else:
                tick_date = max(quote['biddate'], quote['askdate'])

            tick_time = datetime.fromtimestamp(int(tick_date)/1000)
            #print(tick_time, market_open_time)
            if ( tick_time >= market_open_time):
                # SET THAT MARKET IS OPEN
                self.MARKET_OPENED = True
            else:
                # MARKET IS NOT OPEN YET
                return

        g_low =  self._processor.getTickStore(symbol).getLowestTick()
        g_high =  self._processor.getTickStore(symbol).getHighestTick()
        is_high_after_low = self._processor.getTickStore(symbol).isHighAfterLow()
        prev_close = self._processor.getTickStore(symbol).getPrevClose()

        if (self._config['is_backtest']):
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
            self._broker.buy(symbol, quote['ask'], int(self.CAPITAL/quote['ask']) )
            self.profitMap[symbol]['maxProfit'] = 0
            return

        if (ac.checkAndResetSellAllFlag()):
            log().info(dt + " SELL_FLAG_ENABLED Sell ")
            self._broker.sellToClose(symbol, quote['bid'])
            self.profitMap[symbol]['maxProfit'] = 0
            return

        if (ac.hasPosition is False):
            return
            if (len(bars) <= 2):
                return
            if (g_low == bid or g_low == ask): # GONZOLIVE
                if (g_high * 0.75 >= g_low and ac.NUM_UNCLOSED_BUY_TXNS  == 0):
                    log().info(dt + " BUY_AS_FELL_10_PERCENT_FROM_HIGHEST " + str(int(self.CAPITAL/quote['ask'])) + "@" + str(quote['ask']))
                    self._broker.buy(symbol, quote['ask'], int(self.CAPITAL/quote['ask']) )
            '''
            # OR WHAt about buy if price is within a delta of mid high and low ?
            elif (False and ac.NUM_BUY_SELL_LOOPS > 0 and 0.9 * mid <= quote['ask'] <= 1.1 * mid):
                log().info(dt + " BUY_AT_MID_RANGE Buy as are between mid range ")
                self._broker.buy(symbol, quote['ask'], int(self.CAPITAL/quote['ask']) )
            '''
        else: # has position
            # Make these dependent on positions
            avg_price = self._broker.getAC(symbol).cost/self._broker.getAC(symbol).positions
            quantity = int(self._broker.getAC(symbol).positions)
            if (symbol not in self.profitMap):
                self.profitMap[symbol] = {'maxProfit' : 0}
            self.profitMap[symbol]['maxProfit'] = max((quote['bid'] - avg_price) * (ac.positions), self.profitMap[symbol]['maxProfit'])
            log().debug("HAVE POSITION : " + str(data))
            # CHECK IF WE ALREADY ACHIEVED OUR TARGET
            if (quote['bid'] - avg_price >= 10):
                if ( (quote['bid'] - avg_price) * (ac.positions) < self.profitMap[symbol]['maxProfit'] ):
                    log().info(dt + " SELLING_AS_TARGET_ACHIEVED Selling at Profit, Target achieved" + str(ac.positions) + "@" + str(quote['bid']))
                    self._broker.sellToClose(symbol, quote['bid'])
                    self.profitMap[symbol]['maxProfit'] = 0
            # THINK WHAT WE WANT TO DO NOW!!?!?
            # PERHAPS THINK ABOUT INCORPORATING WHAT"s THE MAX CAPITAL WE ARE PUTTING IN
            elif (avg_price - quote['bid'] >= 10):
                log().info(dt + " SELLING_AT_A_LOSS " + str(ac.positions) + "@" + str(quote['ask']))
                self._broker.sellToClose(symbol, quote['bid'])
                self.profitMap[symbol]['maxProfit'] = 0


    def getStrategy(self, symbol = None):
        symbolMap = self._broker.getSymbolMap()
        for sym, ac in symbolMap.items():
            if (symbol is not None):
                if (symbol != sym):
                    continue
            if (ac.hasPosition == False):
                continue

            delta = ac.INTRA_PCT/200
            alpha = 1 - ac.DAILY_ALPHA_PCT/200
            M = ( 1 - alpha * ( 1 + delta) ) / (alpha * delta )

            avg_price = ac.getAvgPrice()
            quantity = ac.getPosition()
            quantity = 1 if quantity < 1 else quantity
            first_buy_capital = avg_price * quantity

            sell_for_profit_price = (2* delta + 1 ) * avg_price
            cent_diff = 2 * delta * avg_price * 100

            second_buy_price = avg_price * alpha
            second_buy_quantity = quantity * M
            second_buy_quantity = 1 if second_buy_quantity < 1 else second_buy_quantity
            second_buy_capital = second_buy_price * second_buy_quantity
            second_buy_cent_dip = (avg_price - second_buy_price ) * 100
            avg_price_post_second_buy = (second_buy_capital + first_buy_capital) / (quantity + second_buy_quantity)

            sell_after_second_buy_price = (2* delta + 1 ) * avg_price_post_second_buy
            cent_diff_for_profit_after_second_buy = (sell_after_second_buy_price - avg_price_post_second_buy) * 100
            expected_profit_after_second_buy = (quantity + second_buy_quantity ) * cent_diff_for_profit_after_second_buy/100

            loss_at_2nd_buy = (avg_price_post_second_buy - second_buy_price) * (quantity + second_buy_quantity)

            targetLowestPrice = (avg_price_post_second_buy/alpha) * (2 * alpha - 1)
            third_buy_price = targetLowestPrice
            third_buy_qty = quantity + second_buy_quantity
            third_buy_cent_dip = (avg_price_post_second_buy - third_buy_price) * 100
            third_buy_capital = third_buy_price * third_buy_qty
            total_capital_post_third_buy = first_buy_capital + second_buy_capital + third_buy_capital
            avg_price_post_third_buy = (total_capital_post_third_buy) / (quantity + second_buy_quantity + third_buy_qty)

            loss_at_3rd_buy = (avg_price_post_third_buy - third_buy_price) * (quantity + second_buy_quantity + third_buy_qty)

            log().info(sym + " Current Quantity is " + str(quantity) + " at " + str(avg_price) + " capital " + str(first_buy_capital))
            log().info(sym + " Sell Target price  " + str(sell_for_profit_price) + " increase of " + str(cent_diff)  + " cents, expected profit " + str(cent_diff*quantity/100) )
            log().info(sym + " 2nd buy Target Price " + str(second_buy_price) + " decrease of " + str(second_buy_cent_dip) + " cents, capital " + str(second_buy_capital) + " Avg price post 2nd buy " + str(avg_price_post_second_buy))
            log().info(sym + " Post 2nd Buy Sell Target price  " + str(sell_after_second_buy_price) + " increase of " + str(cent_diff_for_profit_after_second_buy)  + " cents, expected profit " + str(expected_profit_after_second_buy) )
            log().info(sym + " Loss at 2nd buy " +  str(loss_at_3rd_buy))
            log().info(sym + " 3rd buy Target Price " + str(third_buy_price) + " decrease of " + str(third_buy_cent_dip) + " cents, capital " + str(third_buy_capital) + " Avg price post 3rd buy " + str(avg_price_post_third_buy))
            log().info(sym + " Loss at 3rd buy " +  str(loss_at_3rd_buy))
            log().info(sym + " Max Required Capital " + str(total_capital_post_third_buy) + "\n")
''' Asks

a) Think about this -> Check the max loss/profit based on total positions?
b) Set the expected target profit and play along.
c) [LONG TERM] Find a way to automatically identity stocks to trade
d) Before Buying MORE or SELLING more, see where the stock price is, whether it's near lowest or highest
e) For smaller positions, it's okay to get the default MAX_LOSS/WIN values BUT for higher positions, since the
total pnL could change drastically based on movements, try to see if we can increase the limit based on the position of stock price
f) As time progreses, volatility decreases, try to see if we can reduce our WIN delta to account for that? ( else we will keep holding the pos for long)
g) Get some expected WIN/LOSS dynamically if confident beyond a certain probability, else sell if it touches high and is reverting may be ?
h) Say we are in the money and now based on last few ticks, it could go either ways, decide what to do.
i) ####### How come it was sending orders even before 09:30 ?!!?!?

j) REMOVE THREADS NOT USED, COUNT HOW MANY ARE THERE
i) MOVE LOGGINGS TO LOGGER
j) ENSURE TIMESTAMPS COULD HELP CALCULATING SLIPPAGE
k) Ensure that end of day, we could easily analyze what's went for the day``

L) What happens if cash runs out ? Put something in place to ensure if something like that is aproaching, do something
M) Ensure we take positiosn according to the stock price. Check how it works, i.e. when stock is heavy, vs stock is light, would it affect the buy freq ?
N) We found today that buy quantities we tracked did not match the actual buys! Which is strange. This led to sell orders being rejected as it exceeded the actual available to sell
   We Need to know - a) Why that happened, b) Need some periodic way to sync with tradier's view of our positions, could be with that 10 sec checker
O) Allow TRAP to close out position for a single stock

Q - Does it matter

1) If for three BARS ( VWAP has been decreasing thrice, buy! now if VWAP so far )
'''


## STRATEGY NOTES

'''

Where
Daily = % avg daily diff between high and low ( daily_avg_moves_pct)
Intra = % avg high - low in 1 minutes chart (per_interval_moves_pct )

alpha = 1- Daily%/2
delta = Intra % / 2

Multiplier is =   Q x ( 1 - alpha * ( 1 + delta) )
                         (alpha x delta )

So if price falls to alpha times the original price, buy above many.

We sell if


'''


'''
I wish to begin with, I could tell it to buy and let it do the rest.
Perhaps something like Let it buy on it's own but If I said to buy, it buys instantly, or may be I say to buy at this priuce ?

ALLOW TO SHORT IF AN ETB !

HOW TO EASILY TELL WHAT PRICE IT WILL BUY NEXT and SELL NEXT ?

# 1) Get to choose the change after 11:00 to 12 pm as well!! ?!?
# 2) Get to


# May be split trading in multiple parts -
a) First one would be scalping
b) After a trend is set, may be buy/sell and wait to get a few bucks ?
    *) Eg. declined and now sideways, just buy a bunch with a upper and lower limit orders :)
c) Think of something to do towards the end

# Here's how I think we should do it-
V IMP - AFTER CLOSING A POSITION, wait for some cooling period and try to find the new consolidation point.



### WHAT I NEED HERE -
# So When the TRADING STARTS, I LOOK AT -
    1) Prev pattern which includes the overall sentiments, neutral, bullish, bearish. Yesterday for eg. was Neutral
        Guess one way i do that is by looking at it if by looking at pre markets? Guess if the prices are higher than after hours and the prev days, it's bullish ?
    2) I guess this somehow also includes prev high, low in some way?!
    3) So when i opened, i see, what the current price levels ( i.e. bid and ask look like, where are these going?)
    I also remember seeing the bid/ask quantity.
        a) If ask's quantity has been declining, it will likely go up, thus buy!
        b) If Bid's quantity has been declining, it will likely go up, thus sell!
        So we need to know, given a bid/ask, which one is being hit!? Say at the same  bid price, if only bid quantity is majorly changing, that means it might go temporarily down
        So one signal is if out of bid/ask, ask quantity as been changing, that means there's a local upwards pressure -> Enter by Buying at ask


        I guess I need to get statistics of how many ticks I process per iteration. Breakdown of num quotes vs timesales
        NOW PLEASE RECORD TODAY, so that I could understand what's going on

# ANOTHER THING I AM TRYING TO DO IS THIS -> AFTER IT BUYS THE SECOND TIME, reduce the win rate by half ( or may be some % of that ? ) or if it does not get there in certain time or it goes up and retract ?
# SO HERE's HOW I DO IT, TO ENTER, WATCH, THEN IF IT GOES DOWN by a few cents after hovering at cuurent level for some time, BUY; IF IT GOES UP,

SO LEVELS ( INTRA_PCT) NEED TO CHANGE. IF IT HAS BEEN CONSOLIDATING AROUND FOR SOME TIME, IT MIGHT NOT GO WAY UP FROM THERE, depending on how many cents it has moved, we should adjust our sell limits accordingly

#1) UPDATE LIMITS BEFORE HANDS, SO TAHT WE NEED TO SIMPLY MOVE THE IDX


#1) Find out what's the % decrease after lowest lowes post 10:30

#2) Try to gauge the direction during the day

GYAN!

STATES OF A MARKET ->
Sharp Up
Sharp Down
Slow Up
Slow Down
small oscillations
large oscillations



# TODOS
# REFACTOR THE STRATEGY CONSTRUCTOR TO TAKE IN SYMBOLS!
'''
