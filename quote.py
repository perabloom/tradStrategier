# Version 3.6.1
import requests
from tia.auth import *
from tia.log import *

def getQuote(symbols):
    if (not isinstance(symbols, list)):
        raise Exception("Should be a list naa!")
    response = requests.post('https://api.tradier.com/v1/markets/quotes',
        data={'symbols': ",".join(symbols), 'greeks': 'false'},
        headers=getAuthHeader()
    )
    try:
        if (int(response.headers['X-Ratelimit-Available']) < 10):
            log().critical(response.headers)
    except Exception as e:
        log().critical(response.headers)
        sleep(5)
        response = requests.post('https://api.tradier.com/v1/markets/quotes',
            data={'symbols': ",".join(symbols), 'greeks': 'false'},
            headers=getAuthHeader()
        )
    json_response = response.json()
    #print(response.status_code)
    if json_response['quotes'] is "null":
        return []
    if isinstance(json_response['quotes']['quote'], list):
        return json_response['quotes']['quote']
    else:
        return [json_response['quotes']['quote']]

def getLastPrice(symbol):
    quote = getQuote([symbol])
    #print(quote)
    if (len(quote) > 0):
        return quote[0]['last']
    else:
        return None

'''
[{'symbol': 'FB', 'description': 'Facebook Inc', 'exch': 'Q', 'type': 'stock', 'last': 345.65,
'change': 0.0, 'volume': 77622, 'open': None, 'high': None, 'low': None, 'close': None,
'bid': 345.25, 'ask': 345.4, 'change_percentage': 0.0, 'average_volume': 15005042,
 'last_volume': 1097918, 'trade_date': 1625774401285, 'prevclose': 345.65, 'week_52_high': 358.79,
 'week_52_low': 226.9, 'bidsize': 1, 'bidexch': 'P', 'bid_date': 1625831705000, 'asksize': 1,
 'askexch': 'Q', 'ask_date': 1625831704000, 'root_symbols': 'FB'}]
'''
def example(symbols):
    qs = getQuote(symbols)
    for q in qs:
        print ("\n", q , "\n")
        highest_pct = "{:.2f}".format(100 * (q['high'] - q['open']) / q['open'])
        lowest_pct = "{:.2f}".format(100 * (q['low'] - q['open']) / q['open'])
        current_pct = "{:.2f}".format(100 * (q['last'] - q['open']) / q['open'])
        spread = "{:.2f}".format(q['ask'] - q['bid'])
        print(q['symbol'], "Spread :", spread," Last: " + str(q['last']) +   " Highest_chg: " + str(highest_pct) + "% Lowest_chg: " +  str(lowest_pct) + "% Current: " + str(current_pct) + "%")
        #print(q['symbol'],q['average_volume'])

if __name__ == '__main__':
    symbols = sys.argv[1].strip().split(',')
    example(symbols)
