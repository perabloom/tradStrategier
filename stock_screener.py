# Version 3.6.1
# At a high level,
# We want to be able to screen stocks, ( given a set of symbols may be ?)
# Screen should have criteria
# - All stocks below $20 ? ( ASK THE TRADIER on this )
# - All stocks with high put selling value
# - All stocks with all time lows
# - All stocks that are highly volatile
## I think to being with, I need to supply a list of screened stocks as an inout to some program to trade


## AT a high level, I provide input, of list of symbols, then we subscribe to all the ticks/options data
## at every tick, do whatever trading that needs to be done!!

import requests
import json
import quote as quoteUtil
from tia.auth import *
import string
import search as search
from datetime import datetime

file_name = datetime.now().strftime('%Y-%m-%d.txt')
file_handle = open("Z_SCREENED_STOCKS_" + file_name,"a")

def process(symbol, quote):
    if (quote['last'] is None):
        return
    try:
        if (quote['last'] < 10 and  quote['last'] * 0.9 <= quote['week_52_low'] and quote['average_volume'] >= 500000):# and quote['last'] < 0.5 * quote['week_52_high']):
            print(quote)
            result_string = symbol + " Last: " + str(quote['last']) + " Highest: " + str(quote['week_52_high']) +" Lowest: " + str(quote['week_52_low'])
            print(str(quote) + " " + str(result_string))
            file_handle.write(str(quote) + " " + str(result_string))
            file_handle.write("\n")
    except Exception as e:
        print(e)


def screen(func = process):
    activate = True
    for char in string.ascii_uppercase:
        #if (char == 'A'):
        #    continue
        print(char)
        symbols = search.querySymbols(char, ['stock'])
        print("Total Number of symbols - ", len(symbols))
        for sym in symbols:
            if (sym == "WFC/WDO"):
                activate = True
            if (activate == False):
                continue
            print(sym)
            # get quote and ensure that price is < $30
            quote = quoteUtil.getQuote([sym])
            if (len(quote) <= 0):
                continue
            func(sym, quote[0])

if __name__ == '__main__':
    screen()
