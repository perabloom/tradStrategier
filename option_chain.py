# Version 3.6.1
import requests
from tia.auth import *
import sys as sys

def getOptionExpirations(symbol, includeStrikes):
    response = requests.get('https://api.tradier.com/v1/markets/options/expirations',
        params={'symbol': symbol, 'includeAllRoots': 'true', 'strikes': includeStrikes},
        headers=getAuthHeader()
    )
    json_response = response.json()
    return json_response['expirations']['date']

def getChains(symbol, expiration):
    response = requests.get('https://api.tradier.com/v1/markets/options/chains',
        params={'symbol': symbol,'expiration':expiration , 'greeks': 'false'},
        headers=getAuthHeader()
    )
    print(response.status_code)
    options = response.json()['options']['option']
    return options
#    for option in options:
#        if option['option_type'] == 'call':
#            print (option)

#print(getChains("SPY", '2021-08-13')[0])
