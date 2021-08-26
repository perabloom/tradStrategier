# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *
from datetime import datetime

def getTimeSale(symbol, start = '2021-07-02 09:30', end = '2021-07-02 16:00'):
    response = requests.get('https://api.tradier.com/v1/markets/timesales',
        params={'symbol': symbol, 'interval': 'tick','start': start,'end': end, 'session_filter' : 'open'},
        headers=getAuthHeader()
    )
    print (response.status_code)
    json_response = response.json()
    #json_formatted_str = json.dumps(json_response, indent=2)
    print(response.status_code)
    #print (json_formatted_str)
    #print (json_response)
    print("\n")
    return json_response


def example(symbol):
    sum = 0
    count = 0
    x = getTimeSale(symbol,'2021-08-20 09:30', '2021-08-20 10:30:00' )['series']['data']
    y = getTimeSale(symbol,'2021-08-20 10:30', '2021-08-20 11:30:10' )['series']['data']
    z = getTimeSale(symbol,'2021-08-20 11:30', '2021-08-20 12:30:00' )['series']['data']
    x.extend(y)
    x.extend(z)

    for i in x:
        #print(i)
        #print("\n")
        sum = sum + i['volume']
        count += 1
    print (sum)
    print ("Total Ticks", count)
    return x

if __name__ == '__main__':
    import sys
    example(sys.argv[1])
