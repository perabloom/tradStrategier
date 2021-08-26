# Version 3.6.1
import rsrch_vwap as rsrchVWAPUtil
import etb as etbUtil
import dailyMoves as dailyMovesUtil

from datetime import datetime, timedelta
import sys
import json


def findStocksToShort():
    avg_vol = 500000
    etb = etbUtil.get_etb_between_x_y(2, 9, avg_vol)
    symbol_to_short_res = []
    symbol_to_long_res = []
    for row in etb:
        print(row)
        symbol = row['symbol']
        try:
            df = rsrchVWAPUtil.dailyVWAPs(symbol, False)
        except:
            continue
        last_three_vwap_changes = df.tail(3)['day_pct_chg']
        last_three_vwap_changes = list(last_three_vwap_changes)
        avg = sum(last_three_vwap_changes) / len(last_three_vwap_changes)
        if (avg < -0.75):
            symbol_to_short_res.append(symbol)
        elif (avg > 0.75):
            symbol_to_long_res.append(symbol)

    return symbol_to_short_res, symbol_to_long_res

if __name__ == '__main__':

    to_short, to_long = findStocksToShort()
    print("DECREASING :" , to_short)
    mp = {}
    for symbol in to_short:
        change = dailyMovesUtil.printHistory(symbol, 10) / 100
        mp[symbol] = change
    val = dict(sorted(mp.items(), key=lambda item: item[1]))
    print(val)
    # Write to file!
    suffix = datetime.now().strftime('%Y-%m-%d.txt')
    fileHandle = open('Z_RSRCH_STOCKS_' + suffix, 'a')
    json_object = json.dumps(val)
    fileHandle.write(json_object)

    print("INCREASING : ", to_long)
    mp = {}
    for symbol in to_long:
        change = dailyMovesUtil.printHistory(symbol, 10) / 100
        mp[symbol] = change
    val = dict(sorted(mp.items(), key=lambda item: item[1]))
    print(val)
    # Write to file!
    fileHandle = open('Z_RSRCH_STOCKS_TO_LONG_' + suffix, 'a')
    json_object = json.dumps(val)
    fileHandle.write(json_object)
