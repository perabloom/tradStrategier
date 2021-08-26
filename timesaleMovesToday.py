# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from memoization import cached

@cached
def getTimeSale1Min(symbol, daysBack = 9):
    end = datetime.now()
    start = end - timedelta(days=daysBack)
    start = start.replace(hour=9, minute=30,second=0,microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    #print("Getting 1 min movements for", symbol, "starting", start)
    response = requests.get('https://api.tradier.com/v1/markets/timesales',
        params={'symbol': symbol, 'interval': '1min','start': start, 'session_filter' : 'open'},
        headers=getAuthHeader()
    )
    #print (response.status_code)
    json_response = response.json()
    #json_formatted_str = json.dumps(json_response, indent=2)
    #print(response.status_code)
    #print (json_formatted_str)
    #rint (json_response)
    return json_response

def getTimeSale5Min(symbol, daysBack = 10):
    end = datetime.now()
    start = end - timedelta(days=daysBack)
    start = start.replace(hour=9, minute=30,second=0,microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    print("Getting 5 min movements for", symbol, "starting", start)
    response = requests.get('https://api.tradier.com/v1/markets/timesales',
        params={'symbol': symbol, 'interval': '5min','start': start, 'session_filter' : 'open'},
        headers=getAuthHeader()
    )
    #print (response.status_code)
    json_response = response.json()
    #json_formatted_str = json.dumps(json_response, indent=2)
    #print(response.status_code)
    #print (json_formatted_str)
    #rint (json_response)
    return json_response

def getTimeSale15Min(symbol, daysBack = 40):
    end = datetime.now()
    start = end - timedelta(days=daysBack)
    start = start.replace(hour=9, minute=30,second=0,microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    print("Getting 15 min movements for", symbol, "starting", start)
    response = requests.get('https://api.tradier.com/v1/markets/timesales',
        params={'symbol': symbol, 'interval': '15min','start': start},#, 'session_filter' : 'open'},
        headers=getAuthHeader()
    )
    json_response = response.json()
    return json_response


def ema(values, period):
    values = np.array(values)
    return pd.ewma(values, span=period)[-1]


def movement5m(symbol, mins_post_0930 = 0, duration_in_min = 10):
    count = 0
    days = {}
    g_max_diff = -1
    g_min_diff = 99999
    ts = getTimeSale5Min(symbol)
    for i in ts['series']['data']:
        timestamp = i['timestamp']
        dt = datetime.fromtimestamp(timestamp)
        tot_time = dt.hour * 60 + dt.minute
        day = dt.day
        # 570  = 9 * 60 + 30, 580 = 9 * 60 + 40
        start = 570 + mins_post_0930
        end = start + duration_in_min
        # i.e. between 0930 and 0940
        if (start <= tot_time <= end):
            if day not in days:
                days[day] = {'max' : -1, 'min' : 999999, 'diff' : 0, 'diffs' : [] , 'open' : i['open']}
            days[day]['max'] = max(days[day]['max'], i['high'])
            days[day]['min'] = min(days[day]['min'], i['low'])
            days[day]['diff'] = days[day]['max'] - days[day]['min']
            days[day]['diffs'].append(i['high']  - i['low'])
            g_max_diff = max(g_max_diff, days[day]['diff'])
            g_min_diff = min(g_min_diff,days[day]['diff'])
            #print(i)
        count += 1
    #print ("Total Ticks", count)
    #print (json.dumps(days, indent=4))
    tot = 0
    tot_pct = 0
    count = 0
    diffs = []
    totDiffPerInterval = 0
    totDiffPerInterval_pct = 0
    totDiffsPerIntervalCount = 0
    for val in days.values():
        count += 1
        diffs.append(val['diff'])
        tot += val['diff']
        tot_pct += val['diff']/val['open'] * 100
        for eachdiff in val['diffs']:
            totDiffPerInterval_pct += eachdiff/val['open'] * 100
            totDiffPerInterval += eachdiff
            totDiffsPerIntervalCount += 1
#    df = pd.DataFrame (data = diffs)
#    print("EMA :", df.ema(span=(len(diffs)) ))
    #print ("Min and Max movement (", "{:.3f}".format(g_min_diff), "{:.3f}".format(g_max_diff), ")")
    #print (np.percentile(diffs, 70))
    #print("per : ", totDiffPerInterval/totDiffsPerIntervalCount)
    return {'symbol' : symbol, 'daily_avg_moves' : tot/count, 'per_interval_moves' : totDiffPerInterval/totDiffsPerIntervalCount,
        'daily_avg_moves_pct' : "{:.2f}".format(tot_pct/count), 'per_interval_moves_pct' : "{:.2f}".format(totDiffPerInterval_pct/totDiffsPerIntervalCount)}

#1) Get the max diff between high and low within all the 1 minute intervals for first 10 minutes
#2) Get the Max diff between BOTH the first 5 minutes
#3) Get the max diff during 1st 10 minutes
def movement1m(symbol, mins_post_0930 = 0, duration_in_min = 10):
    count = 0
    days = {}
    g_max_diff = -1
    g_min_diff = 99999
    ts = getTimeSale1Min(symbol)
    for i in ts['series']['data']:
        timestamp = i['timestamp']
        dt = datetime.fromtimestamp(timestamp)
        tot_time = dt.hour * 60 + dt.minute
        day = dt.day
        # 570  = 9 * 60 + 30, 580 = 9 * 60 + 40
        start = 570 + mins_post_0930
        end = start + duration_in_min
        # i.e. between 0930 and 0940
        if (start <= tot_time <= end):
            if day not in days:
                days[day] = {'max' : -1, 'min' : 999999, 'diff' : 0, 'diffs' : [], 'open' : i['open']}
            days[day]['max'] = max(days[day]['max'], i['high'])
            days[day]['min'] = min(days[day]['min'], i['low'])
            days[day]['diff'] = days[day]['max'] - days[day]['min']
            days[day]['diffs'].append(i['high']  - i['low'])
            g_max_diff = max(g_max_diff, days[day]['diff'])
            g_min_diff = min(g_min_diff,days[day]['diff'])
            #print(i)
        count += 1
    #print ("Total Ticks", count)
    #print (json.dumps(days, indent=4))
    tot = 0
    tot_pct = 0
    count = 0
    diffs = []
    totDiffPerInterval = 0
    totDiffPerInterval_pct = 0
    totDiffsPerIntervalCount = 0
    for val in days.values():
        count += 1
        diffs.append(val['diff'])
        tot += val['diff']
        tot_pct += val['diff']/val['open'] * 100
        for eachdiff in val['diffs']:
            totDiffPerInterval_pct += eachdiff/val['open'] * 100
            totDiffPerInterval += eachdiff
            totDiffsPerIntervalCount += 1
#    df = pd.DataFrame (data = diffs)
#    print("EMA :", df.ema(span=(len(diffs)) ))
    #print ("Min and Max movement (", "{:.3f}".format(g_min_diff), "{:.3f}".format(g_max_diff),")")
    #print (np.percentile(diffs, 70))
    #print("per : ", totDiffPerInterval/totDiffsPerIntervalCount)
    return {'symbol' : symbol, 'daily_avg_moves' : tot/count, 'per_interval_moves' : totDiffPerInterval/totDiffsPerIntervalCount,
            'daily_avg_moves_pct' : tot_pct/count, 'per_interval_moves_pct' : totDiffPerInterval_pct/totDiffsPerIntervalCount}



# {'time': '2021-08-11T15:45:00', 'timestamp': 1628711100, 'price': 5.965, 'open': 5.94, 'high': 5.99, 'low': 5.94, 'close': 5.97, 'volume': 699463, 'vwap': 5.960774}
def get15mins(symbol):
    daysBack = 49
    results = getTimeSale15Min(symbol, daysBack)['series']['data']
    days = {}
    res = []
    for i in results:
        #print (i)
        timestamp = i['timestamp']
        dt = datetime.fromtimestamp(timestamp)
        tot_time = dt.hour * 60 + dt.minute
        day = dt.day
        # 570  = 9 * 60 + 30, 580 = 9 * 60 + 40
        # 16:00 -> 16 * 60 = 960
        start = 570 #930
        close = 960
        n10_end = start + 30 # add 30 minutes to 0930
        #if (start <= tot_time < close):
        res.append(i)
    return res

# daily_avg_moves represents the avg daily movement for the each day ( Avg across days for day's max - day's min) for last 20 days
# per_interval_moves represents the avg daily movement for the given time interval ( Avg across intervals , interval's max - interval's min ) every day for last 20 days
# Intervals could be 1 min, 5 min, 15 mins etc

import sys
#print(movement1m(sys.argv[1], 0, 10 ))
#print(movement5m(sys.argv[1], 0, 10 ))

#for i in range (0,240, 10):
#    print(i, movement5m(sys.argv[1], i, i + 10 ))

# what i wanted though was average amount per n minutes ( for eg. 1 minutes )
# What its currently calculating is for each day, gets high - low for first n minutes and averages it out



#for sym in ['TAL', 'WISH', 'PSFE', 'SPY', 'QQQ', 'BCEL', 'FUBO', 'WKHS', 'RIDE', 'NKLA', 'AMC']:
#    val = movement1m(sym, 0, 10)
#    if (float(val['per_interval_moves_pct']) >= 1):
#        print(val)
def example():
    if (len (sys.argv) > 1 and sys.argv[1] is not None):
        for i in range(0,390,10):
            print(movement1m(sys.argv[1], i, 10))
#example()
#print(movement1m(sys.argv[1], 0, 10))

def min15():
    return get15mins(sys.argv[1])


if __name__ == '__main__':
    #print(min15())
    #print(movement1m(sys.argv[1], 0, 10))
    print(getTimeSale1Min(sys.argv[1], 0))
