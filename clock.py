# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *

def getClock(symbol):
    response = requests.get('https://api.tradier.com/v1/markets/clock',
        params={'delayed': 'true'},
        headers=getAuthHeader()
    )
    print (response.status_code)
    json_response = response.json()
    #json_formatted_str = json.dumps(json_response, indent=2)
    print(response.status_code)
    #print (json_formatted_str)
    print (json_response)
    print("\n")
    return json_response



#getClock("NKLA")
