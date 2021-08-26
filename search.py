# Version 3.6.1
import requests
from tia.auth import *
import string

def search(query):
    response = requests.get('https://api.tradier.com/v1/markets/lookup',
        params={ 'q': query, 'types': 'stock'},
        headers=getAuthHeader()
    )
    json_response = response.json()
    return json_response['securities']['security']

def querySymbols(query, tickerTypes):
    results = search(query)
    res = [ value['symbol'] for value in results if value['type'] in (tickerTypes)]
    return res


def example():
    for char in string.ascii_uppercase:
        print(char)
        res = querySymbols(char, ['stock'])
        print(len(res))
        print(res)

#example()
