# Version 3.6.1
import requests
from tia.auth import *
from tia.log import *
import quote as quoteUtil

def etb():
    response = requests.get('https://api.tradier.com/v1/markets/etb',
        params={},
        headers=getAuthHeader()
    )
    try:
        if (int(response.headers['X-Ratelimit-Available']) < 10):
            log().critical(response.headers)
    except Exception as e:
        log().critical(response.headers)
    json_response = response.json()
    print(response.status_code)
    lst = json_response['securities']['security']
    mp = {}
    for l in lst:
        if l['exchange'] not in mp:
            mp[l['exchange']] = 1
        else:
            mp[l['exchange']] += 1
        if l['exchange'] == 'N':
            #print(l)
            pass
    print(mp)
    return lst


# Get ETB list with price range between x and y and avg daily volume more than specified threshold
def get_etb_between_x_y(x, y, avg_vol):
    lst = etb()
    s = [] # To batch requesting quotes for set of symbols
    ct = 0
    res = []
    for i, line in enumerate(lst):
        s.append(line['symbol'])
        if (len(s) < 100 and i + 1 != len(lst)):
            continue
        quotes = quoteUtil.getQuote(s)
        for quote in quotes:
            #print(quote)
            if (quote['bid'] == None or quote['ask'] == None):
                continue
            if (quote['ask'] - quote['bid'] < -1):
                continue
            #mid = (quote['high'] + quote['low']) / 2
            #if (quote['bid'] < mid):
            #    continue
            if (x <= quote['last'] <= y and quote['average_volume'] > avg_vol):
                #print(quote)
                #print(quote['symbol'], quote['last'], quote['average_volume'])
                res.append( {'symbol' :quote['symbol'],'last' : quote['last'],'avg_vol' : quote['average_volume'] })
                ct += 1
        s = []
    print (ct)
    return res





def example1():
    etb()

def example2():
    # including x and y
    avg_vol = 10000
    results = get_etb_between_x_y(2, 9, avg_vol)
    for result in results:
        print(result)

if __name__ == '__main__':
    example2()
