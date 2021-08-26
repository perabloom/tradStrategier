# Version 3.6.1
# At a high level,
# We will be passing in a symbol as input
# Program will do the following
#   - a method will find all the options associated with that symbol
#   - The list returned will then be added to a subscription
#   - As the quotes are received, on every tick, opportunity of arbitrage will be identified and will be sent in as an order
#      in such a way that it's allowed. ( check if BUY a call and SELL a call is supported)


import requests
import json
from tia.auth import *

def get_options_symbols():
  response = requests.get('https://api.tradier.com/v1/markets/options/chains',
      params={'symbol': 'VXX', 'expiration': '2019-05-17', 'greeks': 'true'},
      headers=getAuthHeader()
  )
  json_response = response.json()
  print(response.status_code)
  print(json_response)
