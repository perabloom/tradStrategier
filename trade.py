# Version 3.6.1
import requests
import orders as orders_util
import positions as positions_util
from tia.auth import *
from tia.log import *

### THIS IS PRETTY DANGEROUS ,IF TRUE, WILL SEND REAL ORDERS
DO_NOT_TRADE = False

order = None

def sendOrder(asset_type, symbol, side, quantity, price, order_type, duration, tag):
    global DO_NOT_TRADE
    log().info('Sending order for ' + symbol + " " + str(price) +'@' + str(quantity))
    if (DO_NOT_TRADE == True):
        return
    dta = {'class': asset_type, 'symbol': symbol, 'side': side, 'quantity': quantity, 'price' : price, 'type': order_type, 'duration': duration, 'tag': symbol}
    log().debug(str(dta))
    response = requests.post('https://api.tradier.com/v1/accounts/6YA18634/orders',
        data=dta,
        headers=getAuthHeader()
    )
    log().info(str(response.status_code) + " : " + str(response.json()))
    json_response = response.json()
    return json_response['order']['id']

def sendOptionsMarketOrder(asset_type, symbol, side, quantity, duration, tag, expectedFillPrice):
    global DO_NOT_TRADE
    log().info('Sending ' + side + ' order for ' + symbol + " " + str(quantity) + " at " + str(expectedFillPrice))

    if (DO_NOT_TRADE == True):
        return
    # GONZO
    dta = {'class': asset_type, 'symbol': 'GONZO', 'option_symbol' : symbol, 'side': side, 'quantity': quantity, 'type': 'market', 'duration': duration, 'tag': symbol}
    log().debug(str(dta))
    try:
        response = requests.post('https://api.tradier.com/v1/accounts/6YA18634/orders',
            data=dta,
            headers=getAuthHeader()
        )
    except Exception as e:
        log().critical("*********************CRITICAL : Failed to sendMarketOrder" + str(symbol) + " " + str(e))
        return
    if (response.status_code != 200):
        log().critical("*********************CRITICAL : Bad Status Code for sendMarketOrder " + str(symbol) + " " +  str(response.status_code) + " Content : " + str(response.content))
        return
    log().info(str(response.status_code) + " : " + str(response.json()))
    json_response = response.json()
    return json_response['order']['id']

def sendMarketOrder(asset_type, symbol, side, quantity, duration, tag, expectedFillPrice = None):
    global DO_NOT_TRADE
    if (expectedFillPrice is None):
        log().info('Sending ' + side + ' order for ' + symbol + " " + str(quantity))
    else:
        log().info('Sending ' + side + ' order for ' + symbol + " " + str(quantity) + " at " + str(expectedFillPrice))

    if (DO_NOT_TRADE == True):
        return
    dta = {'class': asset_type, 'symbol': symbol, 'side': side, 'quantity': quantity, 'type': 'market', 'duration': duration, 'tag': symbol}
    log().debug(str(dta))
    try:
        response = requests.post('https://api.tradier.com/v1/accounts/6YA18634/orders',
            data=dta,
            headers=getAuthHeader()
        )
    except Exception as e:
        log().critical("*********************CRITICAL : Failed to sendMarketOrder" + str(symbol) + " " + str(e))
        return
    if (response.status_code != 200):
        log().critical("*********************CRITICAL : Bad Status Code for sendMarketOrder " + str(symbol) + " " +  str(response.status_code) + " Content : " + str(response.content))
        return
    log().info(str(response.status_code) + " : " + str(response.json()))
    json_response = response.json()
    return json_response['order']['id']

def cancelOrder(order_id):
    log().warn('Cancelling order ' + str(order_id))
    response = requests.delete('https://api.tradier.com/v1/accounts/6YA18634/orders/'+str(order_id),
        data={},
        headers=getAuthHeader()
    )
    print (response.status_code)
    json_response = response.json()
    log().info(json_response)

def cancelAllOrders(symbol = None):
    log().warn("Cancelling All Orders")
    if (symbol is None):
        orders = orders_util.getAllOrders()
    else:
        orders = orders_util.getAllOrdersForSymbol(symbol)

    #print (orders)
    count = 0
    if ( isinstance(orders, list)):
        if (len(orders) <= 0):
            return count
    elif (orders['orders'] == "null"):
        return count

    if (isinstance(orders, list)):
        for order in orders:
            try:
                if (order['status'] not in ['expired', 'canceled', 'rejected', 'error', 'filled']):
                    cancelOrder(order['id'])
                    count += 1
            except Exception as e:
                log().error("Error Cancelling Order : " + str(order['id']) + " : " + str(e) )
    # When there's more than 1 order, response is a list
    elif isinstance(orders['orders']['order'], list):
        for order in orders['orders']['order']:
            try:
                if (order['status'] not in ['expired', 'canceled', 'rejected', 'error', 'filled']):
                    cancelOrder(order['id'])
                    count += 1
            except Exception as e:
                log().error("Error Cancelling Order : " + str(order['id']) + " : " + str(e) )
    else: # Else response is a dict
        for key, order in orders['orders'].items():
            try:
                if (order['status'] not in ['expired', 'canceled', 'rejected', 'error', 'filled']):
                    cancelOrder(order['id'])
                    count += 1
            except Exception as e:
                log().error("Error Cancelling Order : " + str(order['id']) + " : " + str(e) )
    return count


def testSendOrder(asset_type, symbol, side, quantity, price, order_type, duration, tag):
    print("testSendOrder")
    print('Sending a ', side, ' order at ',price)
    return 'id'

def closePositions(positions, duration = 'day'):
    for position in positions:
        symbol = position['symbol']
        quantity = position['quantity']
        cost_basis = position['cost_basis']
        if (cost_basis < 0):
            sendMarketOrder('equity', symbol, 'buy_to_cover', -quantity, duration,'closePosition')
        else:
        #TO DO determine the type from symbol
            sendMarketOrder('equity', symbol, 'sell', quantity, duration,'closePosition')

def closeAllPositions():
    print("Closing All Positions")
    positions = positions_util.getAllPositions()
    closePositions(positions)

def getOut():
    cancelAllOrders()
    closeAllPositions()

def getOutForSymbol(symbol):
    cancelAllOrders(symbol)
    positions = positions_util.getPositions(symbol)
    closePositions(positions)

#print(sendOrder('equity', 'FORD', 'buy', 1, 2.10,'market','day', 'FORD'))
#print(sendMarketOrder('equity', 'FORD', 'buy', 1.53,'pre', 'FORD'))
#print(sendOrder('equity', 'SNDL', 'sell', 1, 0.9573,'limit','day', 'SNDL'))
#cancelOrder(9924102)


#cancelAllOrders("FORD")

#getOutForSymbol("WKHS")
