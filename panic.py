# Version 3.6.1
import trade as tradeUtil
import sys



if (len (sys.argv) < 2):
    print ("Cancelling ALL ORDERS AND POSITIONS")
    tradeUtil.getOut()
else:
    for sym in sys.argv[1:]:
        print ("Cancelling ALL ORDERS AND POSITIONS for ", sym)
        tradeUtil.getOutForSymbol(sym)
