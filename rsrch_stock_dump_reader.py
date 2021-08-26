# Version 3.6.1
from datetime import datetime, timedelta
import quote as quoteUtil
import json


suffix = datetime.now().strftime('%Y-%m-%d.txt')
fileHandle = open('Z_RSRCH_STOCKS_' + suffix, 'r')
for stocks in fileHandle:
    s = []
    stocks = list(json.loads(stocks))
    for i, stock in enumerate(stocks):
        s.append(stock)
        if (len(s) < 100 and i + 1 != len(stocks)):
            continue
        quotes = quoteUtil.getQuote(s)
        for q in quotes:
            if (q['ask'] - q['bid'] > 0.02):
                continue
            highest_pct = "{:.2f}".format(100 * (q['high'] - q['open']) / q['open'])
            lowest_pct = "{:.2f}".format(100 * (q['low'] - q['open']) / q['open'])
            current_pct = "{:.2f}".format(100 * (q['last'] - q['open']) / q['open'])
            print(q['symbol'], "Last: " + str(q['last']) +  " Highest_chg: " + str(highest_pct) + "% Lowest_chg: " +  str(lowest_pct) + "% Current: " + str(current_pct) + "%")

    s = []
