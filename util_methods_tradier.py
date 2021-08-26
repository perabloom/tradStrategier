# Version 3.6.1
# At a high level,
# This is a util class. with methods to

import requests
import json
from tia_utils_internal import *

# get all the option symbols for the given ticker ( FROM TRADIER )
def get_options_symbols(stock_ticker):
    print(stock_ticker)
    response = requests.get('https://api.tradier.com/v1/markets/options/lookup',
        params={'underlying': stock_ticker},
        headers=getAuthHeader()
    )
    json_response = response.json()
    #print (json_response)
    if (json_response['symbols'] == None or json_response['symbols'] == "null"):
        print("ERROR : Perhaps invalid symbol: ", stock_ticker)
        return []
    #print(response.status_code)
    symbols_response = [info for info in json_response['symbols'] if info['rootSymbol'] == stock_ticker ]
    if not symbols_response:
        return []
    symbols_response = symbols_response[0]['options']
    num_symbols = len(symbols_response)
    #print(num_symbols)
    #print(symbols_response)
    return symbols_response


## EXAMPLE
def run_example(ticker):
    options = get_options_symbols(ticker)
    if (len(options)>= 2):
        opra = options[0:2]  # Get first symbol and print it's values
        joined_string = ",".join(opra)
        print(joined_string)
        print(get_option_from_occ(options[0]))

#run_example('RAPT')
