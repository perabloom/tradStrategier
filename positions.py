# Version 3.6.1
import requests
from tia.auth import *

def getPositions(symbol):
    positions = getAllPositions()
    return [position for position in positions if position['symbol'] == symbol]

def getAllPositions():
    response = requests.get('https://api.tradier.com/v1/accounts/6YA18634/positions',
        params={},
        headers=getAuthHeader()
    )
    json_response = response.json()
    #print(response.status_code)
    print(json_response)
    if (json_response['positions'] == "null"):
        return []
    if isinstance(json_response['positions']['position'], list):
        return json_response['positions']['position']
    return [json_response['positions']['position']]



def example():
    print(getAllPositions())

#example()
