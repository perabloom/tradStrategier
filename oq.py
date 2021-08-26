# Version 3.6.1
import sys
import requests
import json
from tia.auth import *
from util_methods_tradier import *
from OptionHolder import *
import get_options as getOptions

from timeit import default_timer as timer
from datetime import datetime


def getQuotes(symbol):
  print ("*********** Getting Quotes for ", symbol)
  response = requests.post('https://api.tradier.com/v1/markets/events/session',
      data={},
      headers=getAuthHeader()
  )
  json_response = response.json()
  session_id = json_response['stream']['sessionid']

  opra = []
  symbols = symbol.strip().split(",")
  #opra = get_options_symbols(symbol)
  for symbol in symbols:
    opra.append(symbol)
    options = getOptions.getOptions(symbol,9, True, 9)
    for opt in options:
      opra.append(opt['symbol'])

  joined_string = ",".join(opra)
  #print (f"Joined strings = {joined_string}")

  payload = {
    'sessionid': session_id,
    'symbols': joined_string,
    'linebreak': True
  }

  a = OptionHolder()

  headers = {
    'Accept': 'application/json'
  }
  r = requests.post('https://stream.tradier.com/v1/markets/events', stream=True, data=payload, headers=headers)
  print (r.status_code)

  start = timer()
  suffix = datetime.now().strftime('%Y-%m-%d.txt')
  fileHandle = open('Z_OPTIONS_' + suffix, 'a')
  allowed_types = ['quote', 'timesale']
  for line in r.iter_lines():
    if line:
      #print (line)
      x = json.loads(line)
      if (x['type'] in allowed_types):
        json_object = json.dumps(x)
        fileHandle.write(json_object)
        fileHandle.write("\n")
        #json_formatted_str = json.dumps(json.loads(line), indent=2)
        #print (json_formatted_str)

getQuotes(sys.argv[1]) # symbol
