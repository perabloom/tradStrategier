# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *
from datetime import datetime, timedelta
import etb as etbUtils
import timesaleMoves as timeSaleMovesUtil
import stock_screener as stockScreenerUtil


# This method prints the ETB securities in the given price range and volume
def printETBInRange():
    items = etbUtils.get_etb_between_x_y(5,25,10000000)
    for item in items:
        sym = item['symbol']
        val = timeSaleMovesUtil.movement1m(sym, 0, 10)
        #if (float(val['per_interval_moves_pct']) >= 1):
        print(val)


# Go through each stock, get quote, put it in a file.
# Then next time, read the file and only ask for those with set criteria, so that we don't call api for unimportant stocks
# the idea is to get lastest moves

def dumpAllStockQuotesToFile():
    # Simply dumps to a file
    suffix = datetime.now().strftime('%Y-%m-%d.txt')
    fileHandle = open('Z_STOCKS_DUMP_' + suffix, 'a')
    def dumpToFile(sym, quote):
        json_object = json.dumps(quote)
        fileHandle.write(json_object)
        fileHandle.write("\n")

    # Get a stock with each letterm then applies the passed in function to the output
    stockScreenerUtil.screen(dumpToFile)


def process(quote):
    try:
        suffix = datetime.now().strftime('%Y-%m-%d.txt')
        fileHandle = open('Z_VOL_STOCKS_' + suffix, 'a')
        val = timeSaleMovesUtil.movement1m(quote['symbol'], 0, 10)
        if (float(val['daily_avg_moves_pct']) >= 5):
            quote.update(val)
            json_object = json.dumps(quote)
            fileHandle.write(json_object)
            fileHandle.write("\n")
    except:
        return

# Now we can read from the file
def getStocksWithCriteria(callback = process):
    suffix = datetime.now().strftime('%Y-%m-%d.txt')
    fileHandle = open('Z_STOCKS_DUMP_' + suffix, 'r')
    count = 0
    skipped = 0
    activate = True
    for quote in fileHandle:
        quote = json.loads(quote)
        if (quote['symbol'] == "ICLK"):
            activate = True
        if (activate == False):
            continue
        if (quote['prevclose'] == None or
            quote['prevclose'] == None or
            quote['volume'] in (None, 0) or
            quote['open'] in (None, 0) or
            (quote['last'] is not None and quote['last'] <= 1) ):
            skipped += 1
            continue
        count += 1
        #print(quote)
        callback(quote)
    print('Count', count, ',Skipped', skipped)

if __name__ == '__main__':
    dumpAllStockQuotesToFile()
    getStocksWithCriteria()
