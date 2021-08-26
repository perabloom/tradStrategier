# Version 3.6.1
# At a high level,
# given stock tickers, find out the closest and next closest expiry with high 2-3 strikes down oom put premium


import requests
import json
from tia.auth import *
import util_methods_tradier as tradierUtils
import tia_utils_internal as internalUtils
import quote as quoteUtil
import search as search
import string
from tia.log import *
from datetime import datetime

def getLowerStrikePutOptions(ticker, lastPrice = None, expiryLevels = 2):
    # Get a list of all the option symbols from tradier
    optionInfos = tradierUtils.get_options_symbols(ticker)
    # Parse all the symbols into a structured object
    parsed_opts = [internalUtils.get_option_from_occ(optionInfo) for optionInfo in optionInfos ]
    # Filter out everything except PUTs
    filteredOptionInfos = [x for x in parsed_opts if x['option_type'] =='P']
    # Filter out expiry level beyond the one specified by first fetching the number of near term expiries
    expiries = getFirstNExpiries(filteredOptionInfos, expiryLevels)
    filteredOptionInfos = [ optionInfo for optionInfo in filteredOptionInfos if optionInfo['expiry'] in expiries]
    # Filter out strikes that are ITM or way OOM
    # Get last price and get all the stocks less than 85% and greater than 35% of the last price
    if (lastPrice is None):
        lastPrice = quoteUtil.getLastPrice(ticker)
    filteredOptionInfos = [ optionInfo for optionInfo in filteredOptionInfos if ( (optionInfo['strike'] <= (lastPrice * 0.95) ) and (optionInfo['strike'] >= (lastPrice * 0.35)) )]
    return filteredOptionInfos

def getFirstNExpiries(optionInfos, expiryLevels):
    res =  list(set([optionInfo['expiry'] for optionInfo in optionInfos if optionInfo['expiry'] > datetime.now()]))
    res.sort()
    return list(res)[0:expiryLevels]

def screenOptions(symbol, lastPrice = None, low_52_weeks = ""):
    target_options = getLowerStrikePutOptions(symbol, lastPrice)
    target_options = sorted(target_options, key=lambda val: (val['expiry'], val['strike']), reverse=False)
    file_name = datetime.now().strftime('%Y-%m-%d.txt')
    file_handle = open("PUTS_" + file_name,"a")
    now = datetime.now()
    #print(now)
    for option in target_options:
        occ = option['occ']
        expiry = option['expiry']
        difference = expiry - now
        num_days = difference.days  # REMOVE 1 IF doing for next day, keep it if doing for today
        qt = quoteUtil.getQuote([occ])
        try:
            pct = float("{:.3f}".format(100*(qt[0]['bid']/qt[0]['strike'])))
            daily_return = float("{:.2f}".format(pct/num_days))
            # ANYTHING MORE THAN OR EQUAL TO 1% daily is welcome!!
            if (daily_return >= 0.4):
                result_string = qt[0]['description'] + " : " + str(qt[0]['bid']) + " - " + str(qt[0]['ask']) + " Total Return : " + "{:.2%}".format(qt[0]['bid']/qt[0]['strike']) + ", Daily Return : " + str(daily_return) + "%" + " Lowest - " + str(low_52_weeks)
                file_handle.write(result_string)
                file_handle.write("\n")
                print(result_string)
        except Exception as e:
            print("Error while screening option for symbol - " + symbol + " " + str(e))
            log().error("Error while screening option for symbol - " + symbol + " " + str(e))

    file_handle.close()

def example1(sym):
    screenOptions(sym)

def screen():
    activate = True
    for char in string.ascii_uppercase:
        #if (char == 'A'):
        #    continue
        print(char)
        symbols = search.querySymbols(char, ['stock'])
        print("Total Number of symbols - ", len(symbols))
        for sym in symbols:
            if (sym == "FFWC"):
                activate = True
            if (activate == False):
                continue
            print(sym)
            # get quote and ensure that price is < $30
            quote = quoteUtil.getQuote([sym])

            try:
                lastPrice = quote[0]['last']
                low_52_weeks = quote[0]['week_52_low']
            except:
                continue
            if (lastPrice is None):
                continue
            if (lastPrice >= 30):
                continue
            else:
                screenOptions(sym, lastPrice, low_52_weeks)



#screen()
#example1("CLOV")


def example():
    getLowerStrikePutOptions('WKHS')
