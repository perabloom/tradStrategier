import trade as tradeUtil


while (True):
    x = input(" Command!")
    x = x.strip().split()
    if (len(x) == 2):
        action = 'buy'
        qty = int(x[0])
        symbol = x[1]
        print("sending market order")
        tradeUtil.sendMarketOrder('equity', symbol, action, qty, 'day', symbol)
    elif(len(x) == 3):
        if (x[0] in ( 'b', 'buy') ):
            action = 'buy'
        elif(x[0] in( 's', 'sell') ):
            action = 'sell'
        elif(x[0] in ('ss','short', 'sell_short')):
            action = 'sell_short'
        elif (x[0] in ('c', 'bc', 'cb', 'buy_to_cover', 'btc')):
            action = 'buy_to_cover'
        else:
            print("Invalid Action : ", x[0])
            continue
        qty = int(x[1])
        symbol = x[2]
        tradeUtil.sendMarketOrder('equity', symbol, action, qty, 'day', symbol)
