# Version 3.6.1
import requests
import json
from tia.auth import *
response = requests.get('https://api.tradier.com/v1/accounts/6YA18634/gainloss',
    params={'page': '1', 'limit': '100', 'sortBy': 'closeDate', 'sort': 'desc'
    """ ,'start': '2021-01-01', 'end' : '2021-06-1', 'symbol': 'SNDL' """
    },
    headers=getAuthHeader()
)
json_response = response.json()
print(response.status_code)
print(json_response)

json_formatted_str = json.dumps(json_response, indent=2)
print(json_formatted_str)
