import trade as tradeUtil
import quote_streamer as quoteStreamer
import threading
import json
import traceback

tradeUtil.DO_NOT_TRADE = False
buyMap = {} # 'quantity' , 'low' 'high'  'executed' , 'desiredPrice'

s = quoteStreamer.Streamer()
GLOBAL_FILTER = ['tradex', 'trade', 'summary' ]
ONLY_FILTER = ['quote']
printQuotes = False
# SIMPLY PLACES SYMBOL'S DATA INTO CORRESPONDING QUEUE
def handler(line):
    try:
        global printQuotes
        data = json.loads(line)
        symbol = data['symbol'].upper()
        data_type = data['type']
        #if (data_type in ('trade')):
        #    internalUtils.isStale(line, data['date'])
        # Filter out all that's not timesale/quote
        if (data_type in ONLY_FILTER):
            if (printQuotes):
                print("*** TOP ***", data)
            if ('low' not in buyMap[symbol]):
                return
            if (buyMap[symbol]['executed'] == True):
                bid = data['bid']
                ask = data['ask']
                low = buyMap[symbol]['low']
                high = buyMap[symbol]['high']
                qty = buyMap[symbol]['quantity']
                if (qty > 0):
                    if ( bid <= low or bid >= high):
                        print("Touched bracket, closing it out for " + symbol)
                        tradeUtil.sendMarketOrder('equity', symbol, 'sell', qty, 'day', symbol)
                        del buyMap[symbol]
                        resub(",".join(buyMap.keys()))
                        return
                elif (qty < 0):
                    if ( ask <= low or ask >= high):
                        print("Touched bracket, closing it out for " + symbol)
                        tradeUtil.sendMarketOrder('equity', symbol, 'buy_to_cover', -qty, 'day', symbol)
                        del buyMap[symbol]
                        resub(",".join(buyMap.keys()))
                        return
            else: # if not yet executed
                qty = buyMap[symbol]['quantity']
                price = buyMap[symbol]['desiredPrice']
                bid = data['bid']
                ask = data['ask']
                if ( qty > 0 ):
                    # we want to buy as soon as it gets lower than desiredPrice
                    if (ask <= price):
                        print("Ask is lower than my desired price, buying! " + str(buyMap[symbol]))
                        tradeUtil.sendMarketOrder('equity', symbol, 'buy', qty, 'day', symbol)
                        buyMap[symbol]['executed'] = True
                elif (qty < 0):
                    # we want to sell as soon as it gets higher than desiredPrice
                    if (bid >= price):
                        print("Bid exceeded my desired price, selling short! " + str(buyMap[symbol]))
                        tradeUtil.sendMarketOrder('equity', symbol, 'sell_short', -qty, 'day', symbol)
                        buyMap[symbol]['executed'] = True
    except Exception as e:
        print("ERRR IN HANDLER " + str(e))
        print(traceback.format_exc())






def resub(symbols):
    if (len(symbols) > 0):
        print('Resubscribing ' + symbols)
        t = threading.Thread(target=s.resubscribe,args=(symbols,handler,))
        t.start()
    else:
        print('Resubscribing with no symbols')
        s._resubscribe = True



def forInput():
    global printQuotes
    while (True):
        x = input(" Command!")
        x = x.strip().split()
        added = []
        removed = []
        try:
            if (len(x) == 1 and x[0] == 'help'):
                print ("List of commands here -")
                print ("\n print,p - print live incoming quotes")
                print ("\n noprint,np Stop printing quotes")
                print ("\n buymap,buyMap,bm,mp - Print current Map")
            elif (len(x) == 1 and x[0] in('print', 'p')):
                printQuotes = True
            elif (len(x) == 1 and x[0] in('noprint', 'np')):
                printQuotes = False
            elif(len(x) == 1 and x[0] in ('buymap', 'buyMap','bm', 'mp')):
                for key,value in buyMap.items():
                    print(key, value)
            elif (len(x) == 2 and x[0] =='b'): # DEFAULT BUY
                action = 'buy'
                qty = 100
                symbol = x[1].upper()
                # NOT CHECKING IF IT's ALREADY IN MAP
                print("Sending market order")
                tradeUtil.sendMarketOrder('equity', symbol, action, qty, 'day', symbol)
                if (symbol not in buyMap):
                    buyMap[symbol] = {'quantity' : qty, 'executed' : True}
                    added.append(symbol)
                else:
                    buyMap[symbol]['quantity'] += qty
                    continue
            elif (len(x) == 2 and x[0] =='s'): # DEFAULT BUY
                action = 'sell'
                symbol = x[1].upper()
                if (symbol not in buyMap):
                    print(" SYMBOL NOT IN BUY MAP " + symbol)
                    continue
                elif (buyMap[symbol]['quantity'] == 0):
                    print(" no quantity to sell" + symbol)
                    continue
                qty = buyMap[symbol]['quantity']
                print("Sending market order to sell")
                tradeUtil.sendMarketOrder('equity', symbol, action, qty, 'day', symbol)
                buyMap[symbol]['quantity'] = 0
                continue
            elif (len(x) == 2 and x[0] != 'rm'):
                action = 'buy'
                qty = int(x[0])
                symbol = x[1].upper()
                if (symbol in buyMap):
                    print(symbol + " alreayd in buy map , Quantity :" + str(buyMap[symbol]['quantity']))
                    continue
                else:
                    print("Sending market order")
                    tradeUtil.sendMarketOrder('equity', symbol, action, qty, 'day', symbol)
                    buyMap[symbol] = {'quantity' : qty, 'executed' : True}
                    added.append(symbol)
            elif(len(x) == 3):
                if (x[0] in ( 'buy') ):
                    action = 'buy'
                elif(x[0] in( 'sell') ):
                    action = 'sell'
                elif(x[0] in ('ss','short', 'sell_short')):
                    action = 'sell_short'
                elif (x[0] in ('c', 'bc', 'cb', 'buy_to_cover', 'btc')):
                    action = 'buy_to_cover'
                else:
                    print("Invalid Action : ", x[0])
                    continue
                qty = int(x[1])
                symbol = x[2].upper()
                if (action in('buy', 'sell_short') and symbol in buyMap):
                    print(symbol + " already in buy map , Quantity :" + str(buyMap[symbol]['quantity']))
                    continue
                elif(action in('sell', 'buy_to_cover') and symbol not in buyMap):
                    print(symbol + " not in buy Map")
                    continue
                print("Sending market order")
                tradeUtil.sendMarketOrder('equity', symbol, action, qty, 'day', symbol)
                if (action in ('buy')):
                    buyMap[symbol] = {'quantity' : qty, 'executed' : True}
                    added.append(symbol)
                elif(action in ('sell')):
                    buyMap[symbol]['quantity'] -= qty
                    added.append(symbol)
                elif(action in ('sell_short')):
                    buyMap[symbol] = {'quantity' : -qty, 'executed' : True}
                elif(action in ('buy_to_cover')):
                    buyMap[symbol]['quantity'] += qty
                # finally delete the key if it's quantity is zero
                if (buyMap[symbol]['quantity'] == 0):
                    print ("Removing " + symbol)
                    removed.append(symbol)
                    del buyMap[symbol]
            elif(len(x) == 4 and x[0] in ('bkt', 'bracket', 'range', 'BKT')):
                symbol = x[1].upper()
                low = float(x[2])
                high = float(x[3])
                print("SETTING BRACKETS for " + symbol + " ["+ str(low) + "," + str(high) + "]" )
                buyMap[symbol]['low'] = low
                buyMap[symbol]['high'] = high
            elif( len(x) == 6 and x[0] in ('st', 'ST')): # st PUMP -43 5 4 6
                symbol = x[1]
                qty = int(x[2])
                price = float(x[3])
                low = float(x[4])
                high = float(x[5])
                if (symbol in buyMap):
                    print("SYMBOL ALREADY IN buyMap " + str(symbol))
                    continue
                if ( price < low or price > high or high <= low):
                    print ("Price range is not appropriate [", price, low, high, "]")
                    continue
                buyMap[symbol] = {'quantity' : qty, 'desiredPrice' : price, 'low' : low, 'high' : high, 'executed' : False }
                added.append(symbol)
            elif(len(x) == 2 and x[0] in ('rm')):
                symbol = x[1].upper()
                if (symbol in buyMap):
                    del buyMap[symbol]
                    removed.append(symbol)
            if (len(added) > 0 or len(removed) > 0):
                resub(",".join(buyMap.keys()))
        except Exception as e:
            print("ERROR OCCURED " + str(e))



def run():
    t = threading.Thread(target=forInput,)
    t.start()
    t.join()

run()
