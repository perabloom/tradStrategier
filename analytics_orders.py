
import orders as orderUtil
import json
import sys



def analyzeSymbol(symbol):
    buy = 0
    sell = 0
    orders = orderUtil.getAllOrdersForSymbol(symbol)
    for order in orders:
        if (order['side'] == 'buy'):
            buy += order['exec_quantity']
        elif (order['side'] == 'sell'):
            sell += order['exec_quantity']
    print (symbol, buy, sell)

if __name__ == '__main__':
    analyzeSymbol(sys.argv[1])
