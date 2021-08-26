# Version 3.6.1
import requests
import json
from tia.auth import *
import sys



headers = {
  'Accept': 'application/json'
}

def getHistory(symbol, interval, start_date):
  response = requests.get('https://api.tradier.com/v1/markets/history',
      params={'symbol': symbol, 'interval': interval, 'start': start_date, },
      headers=getAuthHeader()
  )
  print(response.headers)
  json_response = response.json()
  json_formatted_str = json.dumps(json_response, indent=2)
  #print(json_formatted_str)
  return json_response
