# Version 3.6.1
'''
import requests

response = requests.get('https://sandbox.tradier.com/v1/markets/history',
    params={'symbol': 'AAPL', 'interval': 'daily', 'start': '2021-07-01', 'end': '2021-08-23'},
    headers={'Authorization': 'Bearer WYCJI4eQjHrLqasjIeIELB9UeaGP', 'Accept': 'application/json'}
)
json_response = response.json()
print(response.status_code)
print(json_response)
'''


import requests

response = requests.get('https://sandbox.tradier.com/v1/markets/etb',
    params={},
    headers={'Authorization': 'Bearer WYCJI4eQjHrLqasjIeIELB9UeaGP', 'Accept': 'application/json'}
)
json_response = response.json()
print(response.status_code)
print(json_response)
