# Version 3.6.1
import sys as sys
import get_options as getOptionsUtil
from datetime import datetime, timedelta
import timesaleMoves as timesaleMovesUtil




def getMAxOpenInterest():
    options =getOptionsUtil.getOptions(sys.argv[1], 5, True, 6)
    high = 0
    res = None
    nextRes = None
    for option in options:
        if (option['open_interest'] > high):
            high = option['open_interest']
            nextRes = res
            res = option
    print(res,"\n", nextRes)

def getMostTradedOption():
    options = getOptionsUtil.getOptions(sys.argv[1], 5, True, 6)
    maxVol = 0
    maxOption = None
    nextMaxOpt = None
    for option in options:
        sym = option['symbol']
        #print(option, "\n")
        data = timesaleMovesUtil.getTimeSale1Min(sym, 1)['series']['data']
        vol = 0
        for line in data:
            #print (line, "\n")
            vol += line['volume']
        if (maxVol < vol):
            maxVol = vol
            nextMaxOpt = maxOption
            maxOption = option
    print(maxOption, maxVol, "\n", nextMaxOpt)

getMostTradedOption()
