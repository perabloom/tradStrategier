# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *
from datetime import datetime

TICK  = 'tick'
MIN_1 = '1min'
MIN_5 = '5min'
MIN_15 = '15min'

def getTimeSale(symbol, start = '2021-08-13 09:30', end = '2021-08-13 16:00'):
    response = requests.get('https://api.tradier.com/v1/markets/timesales',
        params={'symbol': symbol, 'interval': TICK,'start': start,'end': end, 'session_filter' : 'open'},
        headers=getAuthHeader()
    )
    print (response.status_code)
    json_response = response.json()
    print(response.status_code)
    print("\n")
    return json_response


def example(symbol):
    sum = 0
    count = 0
    for i in getTimeSale(symbol)['series']['data']:
        print(i)
        sum = sum + i['volume']
        count += 1
    print (sum)
    print ("Total Ticks", count)

if __name__ == '__main__':
    import sys
    example(sys.argv[1])
