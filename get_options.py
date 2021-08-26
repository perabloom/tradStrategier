# Version 3.6.1
import sys as sys
import quote as quoteUtil
import option_chain as optionChainUtil
import tia_utils_internal as utils
from datetime import datetime, timedelta

def getNAboveAndBelowTheLast(options,N, last):
    res = []
    higherStrikes = set()
    lowerStrikes = set()
    for option in options:
        occ = utils.get_option_from_occ(option['symbol'])
        # just higher Strike
        if ( occ['strike'] >= last):
            higherStrikes.add(occ['strike'])
        elif (occ['strike'] < last ):
            lowerStrikes.add(-occ['strike'])
    lowerStrikes = sorted(lowerStrikes)
    higherStrikes = sorted(higherStrikes)
    higherStrikes = list(higherStrikes)[:min(N, len(higherStrikes))]
    lowerStrikes = list(lowerStrikes)[:min(N, len(higherStrikes))]

    for option in options:
        occ = utils.get_option_from_occ(option['symbol'])
        if (occ['strike'] in higherStrikes or -occ['strike'] in lowerStrikes ):
            #print ("HERE WE GO ", option)
            res.append(option)
    return res

# Given a symbol, get me 1) Quote of the symbol, 2) get options with nearest expiry at least a week ( 6 days ) away,
# get Put and Call at, just above and just below the current price!
# N represents number of strikes above and below the current price
def getOptions(symbol, N = 1, getNearest = False, expiriesTill = 1):
    quote = quoteUtil.getQuote([symbol])[0]
    if (len(quote) <= 0):
        return
    if (quote['last'] is None):
        return
    last = quote['last']
    print("Last price is ", last)
    expirations = optionChainUtil.getOptionExpirations(symbol, False)
    expirations = expirations[0: 1 + min(max(1,expiriesTill), len(expirations))]

    print (expirations)
    myExpiry = set()
    now = datetime.now()
    for expiry in expirations:
        exp = datetime.strptime(expiry, "%Y-%m-%d")
        if ( getNearest == False and exp - now < timedelta(days=5)):
            continue
        myExpiry.add(exp)
        expiriesTill -= 1
        if (expiriesTill == 0):
            break
    if (len(myExpiry) == 0):
        print ("No expiry found")
        return
    print ("My expiries are :", myExpiry)
    options = []
    for expiry in myExpiry:
        #print("Doing for expiry :", expiry)
        option = optionChainUtil.getChains(symbol, expiry)
        #print(option)
        print("\n")
        options += option
    return getNAboveAndBelowTheLast(options, N, last)


#print(getOptions('RAPT', 1, True, 2))
