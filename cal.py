# Version 3.6.1
import requests
import json
from tia.auth import *
import sys

headers = {
  'Accept': 'application/json'
}

def getCalendar(symbol):
  response = requests.get('https://api.tradier.com/beta/markets/fundamentals/calendars',
      params={'symbols': symbol},
      headers=getAuthHeader()
  )

  json_response = response.json()
  x = json_response[0]
  json_formatted_str = json.dumps(x, indent=2)
  print(json_formatted_str)

def example():
  getCalendar(sys.argv[1])

example()
