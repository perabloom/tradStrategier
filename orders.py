# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *



def getAllOrders():
    response = requests.get('https://api.tradier.com/v1/accounts/6YA18634/orders',
        params={'includeTags': 'true'},
        headers=getAuthHeader()
    )
    json_response = response.json()
    json_formatted_str = json.dumps(json_response, indent=2)
    #print (json_formatted_str)
    return json_response
    #print(response.headers)
    #print(json_response)

def checkOrder(order_id):
    response = requests.get('https://api.tradier.com/v1/accounts/6YA18634/orders/'+str(order_id),
        params={'includeTags': 'true'},
        headers=getAuthHeader()
    )
    json_response = response.json()
    print(response.status_code)
    #print(json_response)
    res = []
    if (json_response['order'] == "null"):
        return res
    if isinstance(json_response['order'], list):
        return json_response['order']
    else:
        return [json_response['order']]

def getAllOrdersForSymbol(symbol):
    orders = getAllOrders()
    res = []
    if (orders['orders'] == "null"):
        return res
    # When there's more than 1 order, response is a list
    if isinstance(orders['orders']['order'], list):
        for order in orders['orders']['order']:
            if (order['symbol'] == symbol):
                res.append(order)
    else: # Else response is a dict
        for key, order in orders['orders'].items():
            if (order['symbol'] == symbol):
                res.append(order)
    #print("RES : ", res)
    return res

def getOrdersIdsWithStateForSymbol(state, symbol):
    orders = getOrdersIdsWithState(state)
    return [order for order in orders if order['symbol'] == symbol]

def getOrdersIdsWithState(state):
    orders = getAllOrders()
    res = []
    if (orders['orders'] == "null"):
        return res
    # When there's more than 1 order, response is a list
    if isinstance(orders['orders']['order'], list):
        for order in orders['orders']['order']:
            if (order['status'] == state):
                res.append(order)
    else: # Else response is a dict
        for key, order in orders['orders'].items():
            if (order['status'] == state):
                res.append(order)
    #print("RES : ", res)
    return res

#print(checkOrder(10480132))
#print(getOrdersIdsWithState('open'))
