# Version 3.6.1
import requests
import json
from tia.auth import *
import sys
from datetime import datetime

headers = {
  'Accept': 'application/json'
}

def getQuotes(symbol,):
  response = requests.post('https://api.tradier.com/v1/markets/events/session',
      data={},
      headers=getAuthHeader()
  )
  json_response = response.json()
  session_id = json_response['stream']['sessionid']

  payload = {
    'sessionid': session_id,
    'symbols': symbol,
    'linebreak': True
  }

  r = requests.get('https://stream.tradier.com/v1/markets/events', stream=True, params=payload, headers=headers)

  #file_object = open('CCXI_data_July_6_8am.txt', 'a',)
  suffix = datetime.now().strftime('%Y-%m-%d.txt')
  file_handle = open("Z_STOCKS_QUOTES_" + suffix, "a")
  allowed_types = ['quote', 'timesale']
  for line in r.iter_lines():
    if line:
      x = json.loads(line)
      if (x['type'] in allowed_types):
        #print(line)
        json_object = json.dumps(x)
        file_handle.write(json_object)
        file_handle.write("\n")


getQuotes(sys.argv[1])
