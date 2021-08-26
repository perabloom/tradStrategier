# Version 3.6.1
import requests
from tia.auth import *

def getSessionKey():
    response = requests.post('https://api.tradier.com/v1/markets/events/session',
        data={},
        headers=getAuthHeader()
    )
    json_response = response.json()
    print(response.status_code)
    print("Received key - ", json_response['stream']['sessionid'])
    return json_response['stream']['sessionid']

def example():
    getSessionKey()

#example()
