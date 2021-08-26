# Version 3.6.1
import requests
from tia.auth import *
from tia.log import *


def getBalance():
    response = requests.get('https://api.tradier.com/v1/accounts/6YA18634/balances',
        params={},
        headers=getAuthHeader()
    )
    json_response = response.json()
    print(response.status_code)
    return json_response['balances']

def example():
    bal = getBalance()
    print(bal)


#example()
