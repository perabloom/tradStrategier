# Version 3.6.1
import timesaleMoves as timesaleMovesUtil
from datetime import datetime, timedelta
import sys


def min15(symbol):
    start = 570 #930
    close = 960
    dates = {}
    rows = timesaleMovesUtil.get15mins(symbol)
    for i in rows:
        timestamp = i['timestamp']
        dt = datetime.fromtimestamp(timestamp)
        strDate = dt.strftime('%Y-%m-%d')
        if strDate not in dates:
            dates[strDate] = {'pre_rows' : [],  'rows' : [], 'open' : None, 'close' : None, 'day_pct_chg' : None, 'high' : -1, 'low' : 9999999, 'pre_high' : -1, 'pre_low' : 9999999}
        tot_time = dt.hour * 60 + dt.minute # In 24 hours format
        if ( tot_time == start): #IF 09:30
            dates[strDate]['open'] = i['open']
        elif (tot_time == close - 15):
            dates[strDate]['close'] = i['close']
            dates[strDate]['day_pct_chg'] = ((i['close'] - dates[strDate]['open']) * 100 ) / dates[strDate]['open']
        if ( tot_time < start): # PRE MARKET all before 09:30
            dates[strDate]['pre_rows'].append(i)
            if ( i['high'] != 'NaN'):
                dates[strDate]['pre_high'] = max(dates[strDate]['pre_high'], i['high'])
            if ( i['low'] != 'NaN'):
                dates[strDate]['pre_low'] = min(dates[strDate]['pre_low'], i['low'])
        elif(tot_time < close): # Normal Market till 16:00
            dates[strDate]['rows'].append(i)
            if ( i['high'] != 'NaN'):
                dates[strDate]['high'] = max(dates[strDate]['high'], i['high'])
            if ( i['low'] != 'NaN'):
                dates[strDate]['low'] = min(dates[strDate]['low'], i['low'])
    print("DONE, NOW ITERATE THROUGH ALL THE DATES")

    for day, rows in dates.items():
        volVWAP = 0
        totalVol = 0
        for row in rows['rows']:
            if (row['volume'] == 0 or row['volume'] == None):
                continue
            totalVol += row['volume']
            volVWAP += row['volume'] * row['vwap']
        dates[day]['vwap'] = volVWAP / max(1,totalVol)
        dates[day]['volume'] =  totalVol
        volVWAP = 0
        totalVol = 0
        for row in rows['pre_rows']:
            if (row['volume'] == 0 or row['volume'] == None):
                continue
            totalVol += row['volume']
            volVWAP += row['volume'] * row['vwap']
        dates[day]['pre_vwap'] = volVWAP / max(1,totalVol)
        dates[day]['pre_volume'] =  totalVol
        dates[day]['volume_ratio'] =  dates[day]['pre_volume'] / max(1,dates[day]['volume'])
    return dates



import pandas as pd
import plotly.express as px
pd.options.plotting.backend = "plotly"
def dailyVWAPs(symbol, doPlot = False):
    dates = min15(symbol)
    data = []
    for key, value in dates.items():
        #print(value)
        #print(key, value['pre_vwap'], value['vwap'], value['volume'])
        data.append([key, value['pre_vwap'], value['vwap'], value['pre_volume'], value['volume'], value['volume_ratio'], value['day_pct_chg'], value['high'], value['low'], value['open'], value['close']])
    df = pd.DataFrame(data, columns=['DATE', 'pre_vwap', 'vwap', 'pre_volume', 'volume', 'volume_ratio', 'day_pct_chg', 'high', 'low', 'open', 'close'])
    #print(df.tail(1))
    df = df[1:-1]
    #df = df.tail(10)
    if (doPlot):
        plot = px.scatter(x=df['DATE'], y=[ df['vwap']])
        plot.show()
        print(df)
    return df

if __name__ == '__main__':
    dailyVWAPs(sys.argv[1], True)
