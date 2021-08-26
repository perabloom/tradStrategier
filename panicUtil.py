# Version 3.6.1
import trade as tradeUtil
import os


def run(symbols = []):
    if (len(symbols) < 1):
        print ("Cancelling ALL ORDERS AND POSITIONS")
        tradeUtil.getOut()
    else:
        for sym in symbols:
            print ("Cancelling ALL ORDERS AND POSITIONS for ", sym)
            tradeUtil.getOutForSymbol(sym)
    os._exit(1)
