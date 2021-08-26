from tia.log import *
from quote_streamer import *
from memoization import cached
from strategies import s_market_make
from strategies import s_stream_only
from strategies import s_momentum
from strategies import s_momentum_run
from strategies import s_momentum_buy_more
from strategies import s_momentum_buy_more_lower_freq
from strategies import s_momentum_profit_or_loss
from strategies import s_momentum_short_sell_profit_or_loss
import threading, queue
import option_screener as opt_screener
import tia_utils_internal as internalUtils
import time
import panicUtil
import positions as positionUtil
import balances as balanceUtil
from datetime import datetime, timedelta
import os

import trade as tradeUtil
tradeUtil.DO_NOT_TRADE = False # False means Trading will be enabled!!
# CURRENT LOG LEVEL
log().setLevel("INFO")

if (tradeUtil.DO_NOT_TRADE is False):
    x = input("DO YOU REALLLY WANT TO ENABLE TRADING?!?!?!? If so, enter 1 : ")
    if (x == "1"):
        log().critical("Running with Trading Enabled")
        log().info(balanceUtil.getBalance())
        pass
    else:
        exit(0)

TARGET_FOR_THE_DAY = 1500
MAX_LOSS_FOR_THE_DAY = -2100

GLOBAL_FILTER = ['tradex', 'trade', 'summary' ]

class Strategies:
    MARKET_MAKE = 0 # Corresponds to s_market_make
    STREAM_ONLY = 1
    BACKTEST = 2
    MOMENTUM = 3
    MOMENTUM_RUN = 4
    MOMENTUM_BUY_MORE = 5
    MOMENTUM_BUY_MORE_LOWER_FREQ = 6
    MOMENTUM_PROFIT_OR_LOSS = 7
    MOMENTUM_SHORT_SELL = 8

# ASSOCIATE STRATEGY WITH QUEUE AND HANDLER
# TODO Refactor to dict eg. {'queue' : q0, 'strategy' : strategy0}
strategyQueueHandlerMap = {
#    Strategies.MARKET_MAKE : (queue.Queue(),s_market_make.MARKET_MAKE()),
#    Strategies.STREAM_ONLY : (queue.Queue(),s_stream_only.STREAM_ONLY()),
#    Strategies.BACKTEST : (queue.Queue(), s_sample_for_backtest.S_BACKTEST()),
#    Strategies.MOMENTUM : ( queue.Queue(), s_momentum.MOMENTUM()),
#    Strategies.MOMENTUM_RUN : ( queue.Queue(), s_momentum_run.MOMENTUM_RUN()),
    #Strategies.MOMENTUM_BUY_MORE : (queue.Queue(), s_momentum_buy_more.MOMENTUM_BUY_MORE()),
    Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ : (queue.Queue(), s_momentum_buy_more_lower_freq.MOMENTUM_BUY_MORE_LOW_FREQ()),
    #Strategies.MOMENTUM_PROFIT_OR_LOSS : (queue.Queue(), s_momentum_profit_or_loss.MOMENTUM_PROFIT_OR_LOSS()),
    Strategies.MOMENTUM_SHORT_SELL : (queue.Queue(), s_momentum_short_sell_profit_or_loss.MOMENTUM_SHORT_SELL_PROFIT_OR_LOSS())

}

# *************************************************************
# MAP TO INDICATE WHICH STRATEGY IS ASSOCIATED WITH EACH SYMBOL
strategyMap = {
    #"BCEL" : [Strategies.MARKET_MAKE],
    #"TAL" :  [Strategies.STREAM_ONLY],
    #"ALF" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    #"TYME" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    #"CIDM" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    "TAL" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    "PSFE" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    "WKHS" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    "WISH" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    "NKLA" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    "BB" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    "RIDE" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    #"PUMP" : [Strategies.MOMENTUM_SHORT_SELL],
    #"COTY" : [Strategies.MOMENTUM_SHORT_SELL],
    #"AVRO" : [Strategies.MOMENTUM_SHORT_SELL],
    #"GEVO" : [Strategies.MOMENTUM_SHORT_SELL],
    #"KDMN" : [Strategies.MOMENTUM_SHORT_SELL],
    #"CLNE" : [Strategies.MOMENTUM_SHORT_SELL],
    #"MESA" : [Strategies.MOMENTUM_SHORT_SELL],
    #"IQ" : [Strategies.MOMENTUM_SHORT_SELL],
    #"CHS" : [Strategies.MOMENTUM_SHORT_SELL],
    #"EVC" : [Strategies.MOMENTUM_SHORT_SELL],
    #"AMC" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    #"SPY210813C00442500" : [Strategies.MOMENTUM_PROFIT_OR_LOSS],
    #"SPY210813C00441000" : [Strategies.MOMENTUM_PROFIT_OR_LOSS],
    #"SPY210813C00443000" : [Strategies.MOMENTUM_PROFIT_OR_LOSS],
    #"SPY210813P00444000" : [Strategies.MOMENTUM_PROFIT_OR_LOSS],
    #"SPY210813P00442000" : [Strategies.MOMENTUM_PROFIT_OR_LOSS],
    #"SPY" : [Strategies.MOMENTUM_PROFIT_OR_LOSS],
    #"SPY210809C00442000" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    #"SPY210809P00441000" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    #"QQQ210811C00367000" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
    #"EDU" : [Strategies.MOMENTUM_BUY_MORE_LOWER_FREQ],
}
#*************************************************************

# Returns all the queues associated with the symbol
@cached
def getQueuesForSymbol(symbol):
    res = []
    # If it's an OCC symbol, overwrite the symbol to be equity
    if internalUtils.isOCCSymbol(symbol):
        symbol = internalUtils.get_option_from_occ(symbol)['symbol']

    if symbol in strategyMap:
        strategies = strategyMap[symbol]
        for strategy in strategies:
            if strategy in strategyQueueHandlerMap:
                res.append(strategyQueueHandlerMap[strategy][0])
    return res

# Iterate through strategyMap and based on the strategies, get all the symbols that's needed
# Eg. we might need specific option chains too!
# FIGURE OUT HOW TO SPECIFY OPTIONS - MAY BE DIFFERENT MAP FOR OPTIONS?
def getTickers():
    tickers = []
    for items in strategyMap.keys():
        tickers.append(items)
    additional_tickers = [] # for eg do we need options as well ?
    for ticker in tickers:
        if ticker not in strategyMap:
            err_msg = "Ticker " + str(ticker) + " not in strategyMap"
            log().critical(err_msg)
            raise Exception(err_msg)
        elif strategyMap[ticker][0] not in strategyQueueHandlerMap:
            err_msg = "Strategy " + str(strategyMap[ticker]) + " not in strategyQueueHandlerMap"
            log().critical(err_msg)
            raise Exception(err_msg)
        elif "OPTION" in strategyQueueHandlerMap[strategyMap[ticker][0]][1].ASSET_TYPES:
            target_options = opt_screener.getLowerStrikePutOptions(ticker, None, 1)
            target_options = sorted(target_options, key=lambda val: (val['expiry'], val['strike']), reverse=False)
            for option in target_options:
                additional_tickers.append(option['occ'])
    tickers.extend(additional_tickers)
    return ",".join(tickers)


# SIMPLY PLACES SYMBOL'S DATA INTO CORRESPONDING QUEUE
def handler(line):
    data = json.loads(line)
    #print("*** TOP ***", data)
    symbol = data['symbol']
    data_type = data['type']
    #if (data_type in ('trade')):
    #    internalUtils.isStale(line, data['date'])
    # Filter out all that's not timesale/quote
    if (data_type in GLOBAL_FILTER):
        return
    queues = getQueuesForSymbol(symbol)
    for q in queues:
        q.put(data)
        #print("QUEUE SIZE : ", q.qsize())

# WORKER THREAD THAT READS FROM THE PASSSED IN QUEUE AND CALLS THE PASSED IN HANDLER
def worker(q, hndlr):
    while True:
        item = q.get()
        #print(f'Working on {item}')
        hndlr(item)
        #print(f'Finished {item}')
        #q.task_done()

# SMART WORKER THREAD THAT READS FROM THE PASSSED IN QUEUE, GETS THE LATEST DATA AND CALLS THE PASSED IN HANDLER
def workerSmart(q,hndlr):
    while True:
        item = q.get()
        while not q.empty():
            item = q.get()
        log().debug(f'Working on {item}')
        hndlr(item)
        log().debug(f'Finished {item}')

# SMART WORKER THREAD THAT READS FROM THE PASSSED IN QUEUE, GETS THE LATEST DATA AND CALLS THE PASSED IN HANDLER
def workerSmarter(q,hndlr):
    while True:
        per_symbol_latest_data = {}
        threads = []
        while not q.empty():
            item = q.get()
            symbol = item['symbol']
            if (symbol not in per_symbol_latest_data):
                per_symbol_latest_data[symbol] = []
            per_symbol_latest_data[symbol].append(item)
        for values in per_symbol_latest_data.values():
            t = threading.Thread(target=hndlr,args=(values,))
            t.start() # WE SHOULD LOG WHERE THIS THROWS!!
            threads.append(t)
        # join all threads
        for t in threads:
            t.join()

# Start consumer threads to read from queue for each strategy
def startConsumers():
    for value in strategyQueueHandlerMap.values():
        threading.Thread(target=workerSmarter, args=(value[0],value[1].hndl,), daemon=False).start()


def handlePOS(symbol = None):
    strats = set()
    for key, values in strategyMap.items():
        if (symbol is not None):
            if (key == symbol):
                for value in values:
                    strats.add(value)
        else:
            for value in values:
                strats.add(value)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        if ( symbol is None):
            st.getBroker().printPnL()
        else:
            st.getBroker().printPnLForSymbol(symbol)

def printLimits(symbol = None):
    strats = set()
    for key, values in strategyMap.items():
        if (symbol is not None):
            if (key == symbol):
                for value in values:
                    strats.add(value)
        else:
            for value in values:
                strats.add(value)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        if ( symbol is None):
            limits = st.getBroker().getLimits()
            for limit in limits:
                print(limit)
        else:
            print(st.getBroker().getLimitsForSymbol(symbol))

def enableBuy(symbol):
    strats = set()
    for key, values in strategyMap.items():
        if (key == symbol):
            for value in values:
                strats.add(value)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        st.getBroker().enableBuy(symbol)

def enableSellAll(symbol):
    strats = set()
    for key, values in strategyMap.items():
        if (key == symbol):
            for value in values:
                strats.add(value)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        st.getBroker().enableSellAll(symbol)

def stopTrading(symbol):
    strats = set()
    for key, values in strategyMap.items():
        if (key == symbol):
            for value in values:
                strats.add(value)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        st.getBroker().stopTrading(symbol)

def printBars(symbol = None):
    strats = set()
    symbols = set()
    for key, values in strategyMap.items():
        if (symbol is not None):
            if (key == symbol):
                for value in values:
                    strats.add(value)
        else:
            for value in values:
                strats.add(value)
                symbols.add(key)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        if (symbol is None):
            # Print tick bars for each symbol
            for sym in symbols:
                if (strat in strategyMap[sym]):
                    tickBars = st.getProcessor().getTickStore(sym).getTickBars()
                    tickBars.printBars()
                    tickBars.plotBars()
        else:
            tickBars = st.getProcessor().getTickStore(symbol).getTickBars()
            tickBars.printBars()
            tickBars.plotBars()

# This guy checks and updates the limits every 10 minutes - based on the avg last 20 days moves for each 10 mins interval
lastLimitUpdatetime = None
def checkAndUpdateLimits():
    global lastLimitUpdatetime
    strats = set()
    symbols = set()
    now = datetime.now()
    minsElapsed = 10 # update it every 'minsElapsed' minutes
    if (lastLimitUpdatetime is not None and  (now - lastLimitUpdatetime < timedelta(seconds=60 * minsElapsed))):
        return
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    if (now < market_open):
        return
    delta = now - market_open
    minsSinceOpen = delta.seconds/60
    for key, values in strategyMap.items():
        for value in values:
            strats.add(value)
            symbols.add(key)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        # Print tick bars for each symbol
        for sym in symbols:
            if (strat in strategyMap[sym]):
                broker = st.getBroker()
                ac = broker.getAC(sym)
                if (ac.lastLimitsUpdate is None):
                    continue
                # check if 10 mins has elapsed since last update
                elif(True or now - ac.lastLimitsUpdate >= timedelta(seconds=60 * minsElapsed)):
                    log().info("Auto Updating ACLimits for " + sym)
                    broker.updateACAutoLimits(sym,minsSinceOpen, minsElapsed )
    lastLimitUpdatetime = now


def printStrategy(symbol = None):
    strats = set()
    for key, values in strategyMap.items():
        if (symbol is not None):
            if (key == symbol):
                for value in values:
                    strats.add(value)
        else:
            for value in values:
                strats.add(value)
    for strat in strats:
        st = strategyQueueHandlerMap[strat][1]
        if ( symbol is None):
            st.getStrategy()
        else:
            st.getStrategy(symbol)

def startInputListner():
    def handle():
        global MAX_LOSS_FOR_THE_DAY
        while (True):
            try:
                x = input()
                y = x.split()
                if ( len(x) == 0):
                    continue
                print (" HANDLER INPUT :- ", x, "\n")
                if (x == "HELP"):
                    print ("List of commands here -")
                    print ("\n POS - Prints Positions for each of the traded tickers")
                    print ("\n POS 'TICKER'- Prints Positions for the passed in 'TICKER'")
                    print ("\n PANIC - Close all the positions and pending orders and exit!")
                    print ("\n LOG LEVEL - Prints the current log level")
                    print ("\n LOG 'NEW_LEVEL' - Updates the level to the specified level")
                    print ("\n MAX_LOSS  'NEGATIVE_VALUE' - Updates the MAX_TOTAL_LOSS to the specified level")
                    print ("\n LIMITS 'TICKER' - Print Limits for all the tickers enabled for trading!")
                    print ("\n UPDATE LIMIT 'TICKER' INTRA_PCT 'FLOAT_PCT_VALUE' - Print Limits for all the tickers enabled for trading!")
                    print ("\n BUY 'TICKER' - Buys the provided ticker for all strategies using that ticker,!")
                    print ("\n STOP 'TICKER' - Stops trading in the specified ticker whatsoever!")
                    print ("\n BARS 'TICKER' - Prints and plots bar chart for the specified ticker")
                    print ("\n ST - Prints the strategy ")
                elif (x == "POS"):
                    print ("Input is ", x)
                    handlePOS()
                elif (len(y) >= 2 and y[0] == "POS"):
                    print("**** Printing position for - ", y[1])
                    if (y[1] in strategyMap):
                        handlePOS(y[1])
                elif (x == "PANIC"):
                    print ("Closing Positions and orders and existing. Please run  python3 panic.py  again just in case :) ")
                    panicUtil.run()
                elif (len(y) >= 2 and y[0] == "LOG"):
                    if (y[1] == "LEVEL"):
                        level = logging.getLevelName(log().getEffectiveLevel())
                        print ("Current Level is", level)
                    elif (y[1] in ["DEBUG", "WARN","INFO", "ERROR", "CRITICAL"]):
                        level = logging.getLevelName(log().getEffectiveLevel())
                        if (level != y[1]):
                            print("Level updated from ", level, "to",y[1])
                            log().setLevel(y[1])
                elif(len(y) >= 2 and y[0] == "MAX_LOSS"):
                    val = int(y[1])
                    if (val > 0):
                        sure = input("Are you sure you want to input a Positive Value?!? ( Press 1 if Yes, else 0)")
                        if (sure == "1"):
                            MAX_LOSS_FOR_THE_DAY = val
                            print("updated MAX LOSS to ",MAX_LOSS_FOR_THE_DAY )
                    else:
                        MAX_LOSS_FOR_THE_DAY = val
                        print("updated MAX LOSS to ",MAX_LOSS_FOR_THE_DAY )
                elif (x == "LIMITS"):
                    print ("Input is ", x)
                    printLimits()
                elif (len(y) >= 5 and y[0] == "UPDATE" and y[1] == "LIMITS"):
                    print("**** UPDATING Limits for - ", y[1])
                    if (y[2] in strategyMap):
                        print("UPDATING")
                        strat = strategyMap[y[2]][0]
                        print(strat)
                        print(strat, strategyQueueHandlerMap[strat])
                        st = strategyQueueHandlerMap[strat][1]
                        broker = st.getBroker()
                        ac = broker.getAC(y[2])
                        ac.INTRA_PCT = 1
                        ac.DAILY_ALPHA_PCT = 2
                elif (len(y) >= 2 and y[0] == "LIMITS"):
                    print("**** Printing Limits for - ", y[1])
                    if (y[1] in strategyMap):
                        printLimits(y[1])
                elif (len(y) >= 2 and y[0] == "BUY"):
                    if (y[1] in strategyMap):
                        print("**** Buying ticker - ", y[1])
                        enableBuy(y[1])
                elif (len(y) >= 2 and y[0] == "SELL"):
                    if (y[1] in strategyMap):
                        print("**** Sell to Close ticker - ", y[1])
                        enableSellAll(y[1])
                elif (len(y) == 2 and y[0] == "STOP"):
                    if (y[1] in strategyMap):
                        print("**** Stop Trading ticker - ", y[1])
                        stopTrading(y[1])
                elif (x == "BARS"):
                    print("**** Printing bars for All tickers ")
                    printBars()
                elif (len(y) >= 2 and y[0] == "BARS"):
                    print("**** Printing bars for ticker - ", y[1])
                    if (y[1] in strategyMap):
                        printBars(y[1])
                elif (x == "ST"):
                    print ("Printing Strategy")
                    printStrategy()
            except  Exception as e:
                log().error(" Encoutered an error :" + str(e), exc_info=True)


    t = threading.Thread(target=handle,)
    t.start()

def startPositionsChecker():
    def handle():
        closing_time = datetime.now().replace(hour=15, minute=56,second=0,microsecond=0)
        opening_time = datetime.now().replace(hour=9, minute=30,second=0,microsecond=0)
        while (True):
            time.sleep(10)
            now = datetime.now()
            log().debug ("Checking Positions")
            strats = set()
            totalPnL = 0
            for key, values in strategyMap.items():
                for value in values:
                    strats.add(value)
            for strat in strats:
                st = strategyQueueHandlerMap[strat][1]
                totalPnL += st.getBroker().getTotalPnLSoFar()
            if (now >= opening_time):
                st.getBroker().logPnL()
                log().info ("Total PnL so far :"  + str(totalPnL))
            if (totalPnL >= TARGET_FOR_THE_DAY):
                log().critical("Reaching the target for the day!! Existing after making a total of : " + str(TARGET_FOR_THE_DAY))
                panicUtil.run()
            elif (totalPnL <= MAX_LOSS_FOR_THE_DAY):
                log().critical("Hit Max Loss for the day :(,  Existing after Losing a total of : " +  str(MAX_LOSS_FOR_THE_DAY))
                panicUtil.run()
            elif (tradeUtil.DO_NOT_TRADE == False and now > closing_time):
                log().critical ("Closing Time!!")
                panicUtil.run()

            checkAndUpdateLimits()
        allPositions = positionUtil.getAllPositions()
        log.info(str(allPositions))
        # Compare the above position with what we have based on our broker. If different ,CRITICAL Log and update the broker perhaps ?
        # write the avg price per the broker and per tradier

    t = threading.Thread(target=handle,).start()



def run():
    log().critical("\n*******Starting new run Now******\n")
    s = Streamer()
    tickers = getTickers()
    log().info("TICKERS :" + ''.join(tickers))
    startConsumers()
    startInputListner()
    startPositionsChecker()
    # Should ideally create as many queues as strategies
    s.subscribe(tickers, handler)





# THIS WILL RUN TRADING!
run()

# GUIDANCE FOR LOGGING
# CRITICAL - ??
# ERROR - ??
# WARN - ??
# INFO - LOG ALL THE TRADING RELATED STUFF
# DEBUG - LOG ANYTHING THAT'S USEFUL ONLY FOR DEBUG


'''
import signal
trap_last_time = None
def received_ctrl_c(signum, stack):
    global trap_last_time
    print("Received Ctrl-C")
    now = time.time()
    if (trap_last_time is None):
        print("FIRST TIME")
        trap_last_time = now
    elif (now - trap_last_time < 3):
        sys.exit(0)
    trap_last_time = now
    doStuffs()

handler = signal.signal(signal.SIGINT, received_ctrl_c)


def doStuffs():
    for symbol, strategy in strategyMap.items():
        strategyQueueHandlerMap[strategy][1].getProcessor().getTickStore(symbol).getTickBars().plotBars()
'''
